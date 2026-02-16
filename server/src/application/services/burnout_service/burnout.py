from app.database import db
from typing import List, Dict

# Computes burnout_mean to normalize data for the frontend.
def calculate_average(scores_list: List[dict]) -> Dict:
    if not scores_list:
        return {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0, "message_count": 0}
    
    total = len(scores_list)
    return {
        "politeness": round(sum(s["politeness"] for s in scores_list) / total, 2),
        "sarcasm": round(sum(s["sarcasm"] for s in scores_list) / total, 2),
        "toxicity": round(sum(s["toxicity"] for s in scores_list) / total, 2),
        "message_count": total
    }

# Performs MongoDB aggregation to compute weighted burnout stats for a team or channel entity.
def calculate_burnout_stats(db_connection, entity_id, entity_type="team"):
    match_filter = {
        "analyzed": True,
        "scores": {"$exists": True}
    }

    if entity_type == "team":
        match_filter["teamId"] = entity_id
    else:
        match_filter["channelId"] = entity_id

    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": None,
            "avg_politeness": {"$avg": "$scores.politeness"},
            "avg_sarcasm": {"$avg": "$scores.sarcasm"},
            "avg_toxicity": {"$avg": "$scores.toxicity"}
        }}
    ]

    results = list(db_connection.messages.aggregate(pipeline))

    if results:
        data = results[0]
        return {
            "politeness": round(data.get("avg_politeness", 0), 4),
            "sarcasm": round(data.get("avg_sarcasm", 0), 4),
            "toxicity": round(data.get("avg_toxicity", 0), 4)
        }
    else:
        return {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}

# Aggregates the burnout metrics for the specific team.
def get_burnout_metrics(team_name: str):
    
    cursor = db.messages.find({
        "teamName": team_name,
        "analyzed": True
    })

    team_scores = []      
    channels_data = {}    

    for msg in cursor:
        if msg.get("scores"):
            score = msg["scores"]
            
            channel_name = msg.get("channelName", "Unknown")

            team_scores.append(score)

            if channel_name not in channels_data:
                channels_data[channel_name] = []
            channels_data[channel_name].append(score)

    channels_breakdown = []
    for c_name, c_scores in channels_data.items():
        channels_breakdown.append({
            "channel": c_name,
            "stats": calculate_average(c_scores)
        })

    return {
        "team": team_name,
        "global_burnout": calculate_average(team_scores),
        "channels": channels_breakdown
    }