from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.models import Channel
from app.dependencies import get_current_user

router = APIRouter(prefix="/channels", tags=["Channels"])

@router.post("/create")
def create_channel(channel: Channel, current_user = Depends(get_current_user)):
    
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed to create channels")

    if db.channels.find_one({"_id": channel.id}):
        raise HTTPException(status_code=400, detail="Channel ID already exists")

    team = db.teams.find_one({"_id": channel.team_name})
    if not team:
        raise HTTPException(status_code=404, detail="Parent Team not found")

    db.channels.insert_one({
        "_id": channel.id,
        "name": channel.name,
        "team_name": channel.team_name,
        "burnout_mean": channel.burnout_mean.model_dump() if channel.burnout_mean else None
    })

    db.teams.update_one(
        {"_id": channel.team_name},
        {"$addToSet": {"channels": channel.id}}
    )

    return {"message": "Channel created", "channel": channel.name, "id": channel.id}

@router.get("/by-team/{team_name}")
def get_channels_by_team(team_name: str):
    channels = list(db.channels.find({"team_name": team_name}))
    return channels