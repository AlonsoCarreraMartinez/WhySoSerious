from fastapi import APIRouter, Depends, HTTPException
from typing import List
from application.dtos import ChannelDashboardResponseDTO
from infrastructure.api.dependencies import get_channel_repository
from infrastructure.api.mappers import map_channel_to_dashboard_dto

router = APIRouter(prefix="/channels", tags=["Channels"])

@router.get("/dashboard", response_model=List[ChannelDashboardResponseDTO])
async def get_dashboard_channels(
    channel_repo = Depends(get_channel_repository)
):
    db_channels = channel_repo.get_all()
    results = [map_channel_to_dashboard_dto(channel) for channel in db_channels]
    results.sort(key=lambda x: x.burnoutScore, reverse=True)
    return results

@router.get("/team/{team_name}", response_model=List[ChannelDashboardResponseDTO])
async def get_team_channels(
    team_name: str,
    channel_repo = Depends(get_channel_repository)
):
    db_channels = channel_repo.get_by_team(team_name)
    return [map_channel_to_dashboard_dto(channel) for channel in db_channels]

@router.get("/{channel_id:path}", response_model=ChannelDashboardResponseDTO)
async def get_channel_detail(
    channel_id: str,
    channel_repo = Depends(get_channel_repository)
):
    channel = channel_repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    return map_channel_to_dashboard_dto(channel)