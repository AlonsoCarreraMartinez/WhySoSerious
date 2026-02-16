from fastapi import APIRouter
from app.database import db

router = APIRouter(prefix="/channels", tags=["Channels"])

# Retrieves the list of channels associated with a specific team to populate the Frontend dashboard.
@router.get("/by-team/{team_name}")
def get_channels_by_team(team_name: str):
    channels = list(db.channels.find({"team_name": team_name}))
    return channels