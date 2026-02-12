import os
import sys
import re
import requests
import msal
from pymongo import MongoClient
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

env_path_backend = os.path.join(current_dir, '.env')
env_path_root = os.path.join(parent_dir, '.env')

if os.path.exists(env_path_backend):
    load_dotenv(env_path_backend)
elif os.path.exists(env_path_root):
    load_dotenv(env_path_root)
else:
    print("Error: .env file not found.")
    sys.exit(1)

CLIENT_ID = os.getenv("AZURE_CLIENT_ID") or os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID = os.getenv("AZURE_TENANT_ID") or os.getenv("TENANT_ID")
MONGO_URI = os.getenv("MONGO_URI")

SCOPES = ["https://graph.microsoft.com/.default"] 
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

TARGET_TEAMS = ["León", "Oviedo", "La Bañeza"] # Filter WhySoSerious Teams

new_messages_count = 0
skipped_messages_count = 0

# Authenticates against Azure AD using MSAL to retrieve an OAuth2 access token.
def get_access_token():
    if not CLIENT_SECRET:
        print("Error: AZURE_CLIENT_SECRET is missing in .env")
        sys.exit(1)

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" in result:
        return result['access_token']
    else:
        print(f"Authentication Error: {result.get('error')}")
        print(f"Description: {result.get('error_description')}")
        sys.exit(1)

# Cleans HTML tags from the message content.
def clean_html(raw_html):
    if not raw_html: return ""
    clean = re.sub('<[^<]+?>', '', raw_html)
    return clean.strip()

# Gets the timestamp of the last message stored in the database for a channel.
def get_last_sync_timestamp(collection, channel_id):
    last_msg = collection.find_one(
        {"channelId": channel_id},
        sort=[("timestamp", -1)]
    )
    if last_msg:
        return last_msg["timestamp"]
    return None

# Saves a message to MongoDB, checking for duplicates by external ID.
def save_message(collection, msg_data, team_info, channel_info):
    global new_messages_count, skipped_messages_count

    body_content = msg_data.get('body', {}).get('content')
    if not body_content: return
    
    text_clean = clean_html(body_content)
    if not text_clean: return

    sender_name = msg_data.get('from', {}).get('user', {}).get('displayName', 'Unknown')
    
    if collection.find_one({"externalId": msg_data['id']}):
        skipped_messages_count += 1
        return

    msg_doc = {
        "externalId": msg_data['id'],
        "content": text_clean,
        "sender": sender_name,
        "timestamp": msg_data['createdDateTime'], 
        "teamId": team_info['id'],
        "teamName": team_info['name'],
        "channelId": channel_info['id'],
        "channelName": channel_info['name'],
        "analyzed": False
    }

    collection.insert_one(msg_doc)
    print(f"      [NEW] Saved: {text_clean[:30]}...")
    new_messages_count += 1

# MAIN.
def main():
    if not MONGO_URI:
        print("Error: MONGO_URI missing in .env")
        return

    client = MongoClient(MONGO_URI)
    db = client["whysoserious_db"]
    collection = db["messages"]

    print("\nAttempting to login as Application Service (Daemon)...")
    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    print("Login successful! Scanning Organization...")

    try:
        url_teams = "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')"
        resp_teams = requests.get(url_teams, headers=headers, timeout=30) 
        if resp_teams.status_code != 200:
            print(f"Error fetching teams: {resp_teams.status_code} - {resp_teams.text}")
            return
        teams = resp_teams.json().get('value', [])
    except Exception as e:
        print(f"Connection Error getting teams: {e}")
        return

    print(f"Found {len(teams)} teams in the organization.")

    for team in teams:
        team_name = team['displayName']
        
        if team_name not in TARGET_TEAMS:
            print(f"Skipping Team: {team_name} (Not in target list)")
            continue

        team_info = {'id': team['id'], 'name': team_name}
        print(f"\nProcessing Team: {team_name}")

        try:
            url_channels = f"https://graph.microsoft.com/v1.0/teams/{team['id']}/channels"
            resp_channels = requests.get(url_channels, headers=headers, timeout=30) 
            
            if resp_channels.status_code != 200:
                print(f"   [ERROR] Could not fetch channels for {team_name}: {resp_channels.status_code}")
                print(f"   Details: {resp_channels.text}")
                continue
                
            channels = resp_channels.json().get('value', [])
        except Exception as e:
            print(f"   [CRITICAL] Error connecting to channels for {team_name}: {e}")
            continue

        for channel in channels:
            channel_info = {'id': channel['id'], 'name': channel['displayName']}
            print(f"   Channel: {channel_info['name']}")

            last_db_date = get_last_sync_timestamp(collection, channel['id'])
            if last_db_date:
                print(f"      -> Last sync: {last_db_date}. Checking updates...")
            else:
                print(f"      -> Initial Load: Fetching FULL history...")

            next_link = f"https://graph.microsoft.com/v1.0/teams/{team['id']}/channels/{channel['id']}/messages?$top=20&$expand=replies"
            
            try:
                while next_link:
                    resp_msgs = requests.get(next_link, headers=headers, timeout=30)
                    
                    if resp_msgs.status_code != 200: 
                        print(f"      Error fetching messages: {resp_msgs.status_code}")
                        break
                    
                    data = resp_msgs.json()
                    messages = data.get('value', [])
                    
                    if not messages: 
                        break

                    next_link = data.get('@odata.nextLink')
                    should_stop_fetching = False

                    for msg in messages:
                        msg_date = msg['createdDateTime']

                        if last_db_date and msg_date <= last_db_date:
                            should_stop_fetching = True
                        
                        if not last_db_date or msg_date > last_db_date:
                            save_message(collection, msg, team_info, channel_info)
                        
                        replies = msg.get('replies', [])
                        if replies:
                            for reply in replies:
                                if last_db_date and reply['createdDateTime'] <= last_db_date:
                                    continue
                                save_message(collection, reply, team_info, channel_info)

                    if should_stop_fetching and last_db_date:
                        break

            except requests.exceptions.Timeout:
                print("      Warning: Connection timed out for this channel. Skipping...")
            except Exception as e:
                print(f"      Error: {e}")

    print("\n" + "="*50)
    print(f"SUMMARY")
    print(f"   - New messages saved: {new_messages_count}")
    print(f"   - Existing messages checked: {skipped_messages_count}")
    print("="*50)

if __name__ == "__main__":
    main()