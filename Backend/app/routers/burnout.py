from fastapi import APIRouter, Depends, HTTPException
from app.services.burnout import get_user_burnout, get_team_burnout
from app.services.auth import get_current_user

router = APIRouter(prefix="/burnout", tags=["Burnout"])


@router.get("/user")
def burnout_by_user(user: str, period: str, current_user=Depends(get_current_user)):
    # Authorization
    if current_user["role"] not in ["admin", "manager"] and current_user["username"] != user:
        raise HTTPException(status_code=403, detail="Not allowed")

    result = get_user_burnout(user, period)
    return {"user": user, "period": period, "burnout": result}


@router.get("/team")
def burnout_by_team(team: str, period: str, current_user=Depends(get_current_user)):
    # Authorization
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Managers or admins only")

    result = get_team_burnout(team, period)
    if result is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return {"team": team, "period": period, "burnout": result}
