from fastapi import APIRouter
from app.database import db
from app.models import Team
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])


# Create a new team in the database.
@router.post("/create")
def create_team(team: Team):
    db.teams.insert_one({
        "_id": team.name,
        "manager": team.manager,
        "members": team.members
    })
    return {"message": "Team created", "team": team}

# Endpoint protected
@router.get("/team-info")
def get_team_info(team: str, current_user = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return {"message": f"Team data for {team}"}


