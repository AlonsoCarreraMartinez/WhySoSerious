from fastapi import APIRouter, Header, Depends, HTTPException
from typing import List
from application.services.auth_service import AuthService
from infrastructure.api.dependencies import get_auth_service, get_team_repository

router = APIRouter(prefix="/teams", tags=["Teams"])

# Fetches teams based on Azure permissions.
@router.get("/dashboard")
async def get_dashboard_data(
    x_user_email: str = Header(None, alias="X-User-Email"),
    auth_service: AuthService = Depends(get_auth_service),
    team_repo = Depends(get_team_repository)
):

    if not x_user_email:
        raise HTTPException(status_code=401, detail="X-User-Email header missing")

    permissions = auth_service.validate_user_access(x_user_email)

    if not permissions["in_org"]:
        raise HTTPException(status_code=403, detail="User not in organization")

    if permissions["is_admin"]:
        return team_repo.get_all()

    if permissions["managed_teams"]:
        results = []
        for team_name in permissions["managed_teams"]:
            team_data = team_repo.get_by_id(team_name)
            if team_data:
                results.append(team_data)
        return results

    return [] 