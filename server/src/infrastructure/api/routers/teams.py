from fastapi import APIRouter, Depends, HTTPException
from typing import List
from application.dtos import TeamDashboardResponseDTO
from infrastructure.api.dependencies import get_team_repository
from infrastructure.api.mappers import map_team_to_dashboard_dto

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/dashboard", response_model=List[TeamDashboardResponseDTO])
async def get_dashboard_data(
    team_repo = Depends(get_team_repository)
):
    db_teams = team_repo.get_all()
    results = [map_team_to_dashboard_dto(team) for team in db_teams]
    results.sort(key=lambda x: x.burnoutScore, reverse=True)
    return results

@router.get("/{team_name}", response_model=TeamDashboardResponseDTO)
async def get_team_detail(
    team_name: str,
    team_repo = Depends(get_team_repository)
):
    team = team_repo.get_by_id(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    return map_team_to_dashboard_dto(team)