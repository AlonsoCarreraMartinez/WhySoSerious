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
TENANT_ID = os.getenv("AZURE_TENANT_ID") or os.getenv("TENANT_ID")
MONGO_URI = os.getenv("MONGO_URI")

SCOPES = ["User.Read", "Team.ReadBasic.All", "ChannelMessage.Read.All", "Group.Read.All"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

new_messages_count = 0
skipped_messages_count = 0

# Authenticates against Azure AD using MSAL to retrieve an OAuth2 access token.
def get_access_token():
    if "HEADLESS_TOKEN" in os.environ:
        return os.environ["HEADLESS_TOKEN"]

    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result: return result['access_token']

    print("\nAttempting to open browser for login...")
    try:
        result = app.acquire_token_interactive(scopes=SCOPES)
    except Exception as e:
        print(f"Interactive login failed: {e}")
        flow = app.initiate_device_flow(scopes=SCOPES)
        print(f"Go to: {flow['verification_uri']}")
        print(f"Code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result['access_token']
    else:
        print(f"Error: {result.get('error_description')}")
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

    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}

    print("\nStarting extraction (Optimized Deep Check Strategy)...")

    try:
        resp_teams = requests.get("https://graph.microsoft.com/v1.0/me/joinedTeams", headers=headers, timeout=10)
        teams = resp_teams.json().get('value', [])
    except Exception as e:
        print(f"Error getting teams: {e}")
        return

    print(f"Found {len(teams)} teams.")

    for team in teams:
        team_info = {'id': team['id'], 'name': team['displayName']}
        print(f"\nProcessing Team: {team_info['name']}")

        try:
            url_channels = f"https://graph.microsoft.com/v1.0/teams/{team['id']}/channels"
            resp_channels = requests.get(url_channels, headers=headers, timeout=10)
            channels = resp_channels.json().get('value', [])
        except:
            continue

        for channel in channels:
            channel_info = {'id': channel['id'], 'name': channel['displayName']}
            print(f"   Channel: {channel_info['name']}")

            last_db_date = get_last_sync_timestamp(collection, channel['id'])
            if last_db_date:
                print(f"      -> Last sync: {last_db_date}. checking updates...")
            else:
                print(f"      -> Initial Load: Fetching history...")

            next_link = f"https://graph.microsoft.com/v1.0/teams/{team['id']}/channels/{channel['id']}/messages?$top=20&$expand=replies"
            
            try:
    
                while next_link:
                    resp_msgs = requests.get(next_link, headers=headers, timeout=15) 
                    
                    if resp_msgs.status_code != 200: 
                        print(f"      Error fetching messages: {resp_msgs.status_code}")
                        break
                    
                    data = resp_msgs.json()
                    messages = data.get('value', [])
                    if not messages: break

                    for msg in messages:
                        msg_date = msg['createdDateTime']

                        if not last_db_date or msg_date > last_db_date:
                            save_message(collection, msg, team_info, channel_info)
                        
                        replies = msg.get('replies', [])
                        if replies:
                            
                            for reply in replies:
                                if last_db_date and reply['createdDateTime'] <= last_db_date:
                                    continue
                                save_message(collection, reply, team_info, channel_info)

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