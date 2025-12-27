from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from app.database import db
from dateutil import parser
from app.dependencies import get_current_user

router = APIRouter(prefix="/burnout", tags=["Burnout"])

def get_cutoff_date(period: str):
    now = datetime.utcnow()
    try:
        num = int(period[:-1])
        unit = period[-1]
        
        if unit == 'd': return now - timedelta(days=num)
        if unit == 'w': return now - timedelta(weeks=num)
        if unit == 'm': return now - timedelta(days=30*num)
    except:
        pass 
    return now - timedelta(weeks=1)

def calculate_average(scores_list):
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
def get_team_burnout(team: str, period: str = "1w", current_user = Depends(get_current_user)):
    
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    team_doc = db.teams.find_one({"_id": team})
    if not team_doc:
        raise HTTPException(status_code=404, detail="Team not found")
    
    members = team_doc.get("members", []) 
    cutoff = get_cutoff_date(period)

    cursor = db.messages.find({
        "sender": {"$in": members}, 
        "analyzed": True
    })

    valid_scores = []
    for msg in cursor:
        try:
            msg_date = parser.parse(msg["timestamp"]).replace(tzinfo=None)
            
            if msg_date >= cutoff:
                if msg.get("scores"): 
                    valid_scores.append(msg["scores"])
        except Exception:
            continue 

    return {
        "team": team,
        "period": period,
        "burnout": calculate_average(valid_scores)
    }

@router.get("/user")
def get_user_burnout(user: str, period: str = "1w", current_user = Depends(get_current_user)):
    
    if current_user["role"] not in ["admin", "manager"] and current_user["username"] != user:
        raise HTTPException(status_code=403, detail="Not allowed")

    cutoff = get_cutoff_date(period)

    cursor = db.messages.find({
        "sender": user, 
        "analyzed": True
    })

    valid_scores = []
    for msg in cursor:
        try:
            msg_date = parser.parse(msg["timestamp"]).replace(tzinfo=None)
            if msg_date >= cutoff and msg.get("scores"):
                valid_scores.append(msg["scores"])
        except:
            continue

    return {
        "user": user,
        "period": period,
        "burnout": calculate_average(valid_scores)
    }