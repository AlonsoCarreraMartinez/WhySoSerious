from app.database import db
from typing import List, Dict

# Computes burnout_mean for sentiment scores to normalize data for the frontend.
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

# Queries raw messages from MongoDB, groups them by channel, and aggregates the statistical burnout metrics for the specific team.
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