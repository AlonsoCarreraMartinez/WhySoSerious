from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.database import db

# Define the router
router = APIRouter(prefix="/burnout", tags=["Burnout"])

# Converts strings like '1w', '3d', '1m' into a timedelta.
def parse_period(period: str):
    num = int(period[:-1])
    unit = period[-1]

    if unit == "d":
        return timedelta(days=num)
    if unit == "w":
        return timedelta(weeks=num)
    if unit == "m":
        return timedelta(days=30*num)  # approx monthly

    raise ValueError("Invalid period format. Use '1w', '3d', '1m', etc.")

# Receives a list of scores objects: [{politeness, sarcasm, toxicity}] and computes average burnout indicators.
def compute_burnout(scores_list: list):
    
    if not scores_list:
        return {"politeness": 0, "sarcasm": 0, "toxicity": 0}

    avg = {
        "politeness": sum(s["politeness"] for s in scores_list) / len(scores_list),
        "sarcasm": sum(s["sarcasm"] for s in scores_list) / len(scores_list),
        "toxicity": sum(s["toxicity"] for s in scores_list) / len(scores_list)
    }

    return avg


def get_user_burnout(username: str, period: str):
    delta = parse_period(period)
    now = datetime.utcnow()
    cutoff = now - delta

    blocks = db.message_blocks.find({
        "start_time": {"$gte": cutoff},
        "participants": username
    })

    scores_list = []

    for block in blocks:
        for msg in block["messages"]:
            if msg["user"] == username:
                scores_list.append(msg["scores"])

    return compute_burnout(scores_list)


def get_team_burnout(team_name: str, period: str):
    team = db.teams.find_one({"_id": team_name})
    if not team:
        return None

    delta = parse_period(period)
    now = datetime.utcnow()
    cutoff = now - delta

    blocks = db.message_blocks.find({
        "start_time": {"$gte": cutoff},
        "participants": {"$in": team["members"]}
    })

    scores_list = []

    for block in blocks:
        if "aggregated_scores" in block:
            scores_list.append(block["aggregated_scores"])

    return compute_burnout(scores_list)

# Public endpoint for the Team Dashboard
@router.get("/team")
def burnout_by_team(team: str, period: str):
    
    result = get_team_burnout(team, period)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Team not found")
        
    return {"team": team, "period": period, "burnout": result}

@router.get("/user")
def burnout_by_user(user: str, period: str):
    return {"message": "Use the /team endpoint for the team dashboard"}