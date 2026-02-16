from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.dependencies import get_current_user
from app.services.burnout import get_burnout_metrics 

router = APIRouter(prefix="/burnout", tags=["Burnout"])

# Retrieves real-time burnout analytics. 
@router.get("/team")
def get_team_burnout_endpoint(team: str, current_user = Depends(get_current_user)):

    team_doc = db.teams.find_one({"_id": team})
    if not team_doc:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if current_user["role"] != "admin":
        if team_doc.get("manager") != current_user["_id"]:
             raise HTTPException(status_code=403, detail="Not authorized to view this team's analytics")

    results = get_burnout_metrics(team)

    return results