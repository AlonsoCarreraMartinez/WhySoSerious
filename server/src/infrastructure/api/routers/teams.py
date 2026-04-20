from fastapi import APIRouter, Depends, HTTPException
from typing import List
from application.dtos import TeamDashboardResponseDTO
from infrastructure.api.dependencies import get_team_repository
from infrastructure.api.mappers import map_team_to_dashboard_dto
from infrastructure.api.security import get_current_user, verify_team_access

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/dashboard", response_model=List[TeamDashboardResponseDTO])
async def get_dashboard_data(
    team_repo = Depends(get_team_repository),
    current_user: dict = Depends(get_current_user)
):
    db_teams = team_repo.get_all()
    
    if not current_user.get("is_admin"):
        managed_teams = [t["name"] for t in current_user.get("managed_teams", [])]
        db_teams = [t for t in db_teams if t.name in managed_teams]

    results = [map_team_to_dashboard_dto(team) for team in db_teams]
    results.sort(key=lambda x: x.burnoutScore, reverse=True)
    return results

@router.get("/{team_name}", response_model=TeamDashboardResponseDTO)
async def get_team_detail(
    team_name: str,
    team_repo = Depends(get_team_repository),
    current_user: dict = Depends(get_current_user)
):
    verify_team_access(team_name, current_user)

    team = team_repo.get_by_id(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    return map_team_to_dashboard_dto(team)