import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

# Calculate and update burnout mean of teams and channels.
def calculate_and_update_metrics():
    if not MONGO_URI:
        print("ERROR: MONGO_URI not found")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    teams_collection = db["teams"]
    channels_collection = db["channels"]
    messages_collection = db["messages"]

    print("--- Updating TEAMS (By Name) ---")
    
    team_pipeline = [
        {
            "$match": {
                "analyzed": True,
                "scores": {"$exists": True},
                "teamName": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$teamName",  
                "avg_politeness": {"$avg": "$scores.politeness"},
                "avg_sarcasm": {"$avg": "$scores.sarcasm"},
                "avg_toxicity": {"$avg": "$scores.toxicity"}
            }
        }
    ]

    team_results = list(messages_collection.aggregate(team_pipeline))
    teams_updated_count = 0

    for result in team_results:
        team_name = result["_id"]
        if not team_name: continue

        burnout_mean = {
            "politeness": round(result["avg_politeness"], 2),
            "sarcasm": round(result["avg_sarcasm"], 2),
            "toxicity": round(result["avg_toxicity"], 2)
        }

        update_result = teams_collection.update_one(
            {"_id": team_name}, 
            {"$set": {"burnout_mean": burnout_mean}}
        )
        
        if update_result.matched_count > 0:
            print(f"Team: {team_name} -> Updated metrics: {burnout_mean}")
            teams_updated_count += 1
        else:
            print(f"WARNING: Metrics calculated for Team '{team_name}', but not found in 'teams' collection.")

    print(f"Total Teams updated: {teams_updated_count}")

    print("\n--- Updating CHANNELS (By ID) ---")
    
    channel_pipeline = [
        {
            "$match": {
                "analyzed": True,
                "scores": {"$exists": True},
                "channelId": {"$ne": None} 
            }
        },
        {
            "$group": {
                "_id": "$channelId", 
                "avg_politeness": {"$avg": "$scores.politeness"},
                "avg_sarcasm": {"$avg": "$scores.sarcasm"},
                "avg_toxicity": {"$avg": "$scores.toxicity"}
            }
        }
    ]

    channel_results = list(messages_collection.aggregate(channel_pipeline))
    
    for result in channel_results:
        channel_id = result["_id"]
        if not channel_id: continue

        
        burnout_mean = {
            "politeness": round(result["avg_politeness"], 2),
            "sarcasm": round(result["avg_sarcasm"], 2),
            "toxicity": round(result["avg_toxicity"], 2)
        }

        channels_collection.update_one(
            {"_id": channel_id},
            {"$set": {"burnout_mean": burnout_mean}}
        )
        
    
        print(f"Channel ID: {channel_id[:20]}... updated with {burnout_mean}")

    print("\nFinished updating all statistics.")

if __name__ == "__main__":
    calculate_and_update_metrics()