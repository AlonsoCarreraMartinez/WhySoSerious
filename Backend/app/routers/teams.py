from fastapi import APIRouter
from app.database import db
from app.models import Team
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])


# Create a new team in the database.
@router.post("/create")
def create_team(team: Team, current_user = Depends(get_current_user)):
   
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed to create teams")

    if db.teams.find_one({"_id": team.name}):
        raise HTTPException(status_code=400, detail="Team already exists")

    db.teams.insert_one({
        "_id": team.name, 
        "name": team.name, 
        "manager": team.manager,
        "members": team.members,
        "channels": team.channels,
        "burnout_mean": team.burnout_mean.model_dump() if team.burnout_mean else None
    })
    return {"message": "Team created", "team": team.name}


@router.get("/team-info")
def get_team_info(team: str, current_user = Depends(get_current_user)):
   
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    team_data = db.teams.find_one({"_id": team})
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found")

    return {"message": f"Team data for {team}", "data": team_data}

'''
@router.get("/dashboard", response_model=list)
def get_dashboard_data():
    teams = list(db.teams.find({}, {"_id": 1, "burnout_mean": 1}))
    return teams'''

@router.get("/dashboard") 
def get_dashboard_data():
    pipeline = [
        {
            "$lookup": {
                "from": "channels",
                "localField": "channels",
                "foreignField": "_id",
                "as": "channel_details"
            }
        },
        {
            "$project": {
                "_id": 1,
                "burnout_mean": 1,
                "channel_details": 1 
            }
        }
    ]
    
 
    teams = list(db.teams.aggregate(pipeline))    
    return teams

