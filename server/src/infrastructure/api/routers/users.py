from fastapi import APIRouter, Depends, HTTPException
from typing import List
from application.dtos import MemberResponseDTO
from infrastructure.api.dependencies import get_user_repository, get_team_repository, get_channel_repository
from infrastructure.api.mappers import map_user_to_member_dto
from infrastructure.api.security import get_current_user, verify_team_access

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/team/{team_name}", response_model=List[MemberResponseDTO])
async def get_team_members(
    team_name: str,
    team_repo = Depends(get_team_repository),
    user_repo = Depends(get_user_repository),
    current_user: dict = Depends(get_current_user)
):
    verify_team_access(team_name, current_user)

    team = team_repo.get_by_id(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_users = user_repo.get_by_ids(team.members)
    
    return [
        map_user_to_member_dto(user, getattr(user, 'email', '') in team.managers) 
        for user in db_users
    ]

@router.get("/channel/{channel_id}", response_model=List[MemberResponseDTO])
async def get_channel_members(
    channel_id: str,
    channel_repo = Depends(get_channel_repository),
    team_repo = Depends(get_team_repository),
    user_repo = Depends(get_user_repository),
    current_user: dict = Depends(get_current_user)
):
    channel = channel_repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    verify_team_access(channel.team_name, current_user)
        
    team = team_repo.get_by_id(channel.team_name)
    managers = team.managers if team else []

    db_users = user_repo.get_by_ids(channel.members)
    
    return [
        map_user_to_member_dto(user, getattr(user, 'email', '') in managers) 
        for user in db_users
    ]