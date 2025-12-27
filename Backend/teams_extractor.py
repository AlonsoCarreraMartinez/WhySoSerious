import requests
from msal import PublicClientApplication
from pymongo import MongoClient
import sys
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

env_path_current = os.path.join(current_dir, '.env')
if os.path.exists(env_path_current):
    print(f"Loaded .env from: {env_path_current}")
    load_dotenv(env_path_current)
else:

    env_path_parent = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path_parent):
        print(f"Loaded .env from: {env_path_parent}")
        load_dotenv(env_path_parent)
    else:
        print("ERROR: .env file not found in Backend/ or root folder.")

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
MONGO_URI = os.getenv("MONGO_URI")

SCOPES = ["Chat.Read", "User.Read"]
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"

DB_NAME = "whysoserious_db"
COLLECTION_NAME = "messages"

def main():
    if not MONGO_URI:
        print("ERROR: MONGO_URI missing in .env")
        return
    if not CLIENT_ID or not TENANT_ID:
        print("ERROR: AZURE_CLIENT_ID or AZURE_TENANT_ID missing in .env")
        return

    print("Starting Extraction...")

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
    print("Please log in via the browser pop-up...")
    
    try:
        result = app.acquire_token_interactive(scopes=SCOPES, port=5000)
    except Exception as e:
        print(f"Error initializing login: {e}")
        return

    if "access_token" not in result:
        print(f"Authentication failed: {result.get('error_description')}")
        return

    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Authentication successful.")

    print("Fetching chats...")
    try:
        chats_resp = requests.get("https://graph.microsoft.com/v1.0/me/chats", headers=headers)
        chats = chats_resp.json().get("value", [])
        print(f"Found {len(chats)} chats.")
    except Exception as e:
        print(f"Error connecting to Graph API: {e}")
        return

    messages_to_save = []
    
    for chat in chats:
        c_id = chat['id']
        msgs_url = f"https://graph.microsoft.com/v1.0/me/chats/{c_id}/messages"
        msgs_resp = requests.get(msgs_url, headers=headers)
        
        if msgs_resp.status_code == 200:
            msgs = msgs_resp.json().get("value", [])
            for m in msgs:
                if m.get('body', {}).get('content'):
                    
                    sender_name = "Unknown"
                    from_data = m.get('from')
                    
                    if from_data and isinstance(from_data, dict):
                        user_data = from_data.get('user')
                        if user_data and isinstance(user_data, dict):
                            sender_name = user_data.get('displayName', 'Unknown')
                    
                    msg_obj = {
                        "externalId": m['id'],
                        "content": m['body']['content'],
                        "sender": sender_name,
                        "timestamp": m['createdDateTime'],
                        "platform": "Teams Real (E5)",
                        "analyzed": False
                    }
                    messages_to_save.append(msg_obj)

    print(f"Processed {len(messages_to_save)} valid text messages.")

    if messages_to_save:
        client = None
        try:
            print("Connecting to MongoDB Atlas...")
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]
            coll = db[COLLECTION_NAME]
            
            client.admin.command('ping')
            print("MongoDB Connection OK.")
            
            new_count = 0
            for msg in messages_to_save:
                res = coll.update_one(
                    {"externalId": msg["externalId"]}, 
                    {"$set": msg}, 
                    upsert=True
                )
                if res.upserted_id:
                    new_count += 1
            
            print("------------------------------------------------")
            print(f"SUCCESS: {new_count} new messages inserted into Atlas.")
            print(f"Total in collection: {coll.count_documents({})}")
            print("------------------------------------------------")
            
        except Exception as e:
            print(f"Database Error: {e}")
        finally:
            if client:
                client.close()
    else:
        print("No messages found to save.")

if __name__ == "__main__":
    main()