import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

def calculate_and_update_team_means():
    if not MONGO_URI:
        print("ERROR: MONGO_URI not found")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    teams_collection = db["teams"]
    messages_collection = db["messages"]

    pipeline = [
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

    print("Aggregating message scores...")
    results = list(messages_collection.aggregate(pipeline))
    
    teams_with_data = set()

    for result in results:
        team_name = result["_id"]
        if not team_name:
            continue

        teams_with_data.add(team_name)

        burnout_mean = {
            "politeness": round(result["avg_politeness"], 4),
            "sarcasm": round(result["avg_sarcasm"], 4),
            "toxicity": round(result["avg_toxicity"], 4)
        }

        teams_collection.update_one(
            {"_id": team_name},
            {"$set": {"burnout_mean": burnout_mean}}
        )
        
        print(f"Team: {team_name} updated with {burnout_mean}")

    all_teams = teams_collection.find({}, {"_id": 1})
    
    for team in all_teams:
        if team["_id"] not in teams_with_data:
            empty_scores = {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}
            teams_collection.update_one(
                {"_id": team["_id"]},
                {"$set": {"burnout_mean": empty_scores}}
            )
            print(f"Team: {team['_id']} set to default 0.0 values")

    print("Finished updating team statistics.")

if __name__ == "__main__":
    calculate_and_update_team_means()