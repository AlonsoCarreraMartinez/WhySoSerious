from fastapi import APIRouter, HTTPException
from app.database import db
from typing import List, Dict

router = APIRouter(prefix="/burnout", tags=["Burnout"])

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

@router.get("/team")
def get_team_burnout(team: str):
    
    team_doc = db.teams.find_one({"_id": team})
    if not team_doc:
        raise HTTPException(status_code=404, detail="Team not found")
    
    cursor = db.messages.find({
        "teamName": team,
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
        "team": team,
        "global_burnout": calculate_average(team_scores),
        "channels": channels_breakdown
    }