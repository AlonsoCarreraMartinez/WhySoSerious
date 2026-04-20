from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from application.dtos import HistoricalDataPointDTO
from infrastructure.api.dependencies import get_burnout_repository, get_team_repository, get_channel_repository
from infrastructure.api.mappers import map_trend_to_historical_dto
from infrastructure.api.security import get_current_user, verify_team_access

router = APIRouter(prefix="/burnout", tags=["Burnout"])

@router.get("/historical/{target_name}", response_model=List[HistoricalDataPointDTO])
async def get_historical_data(
    target_name: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    burnout_repo = Depends(get_burnout_repository),
    team_repo = Depends(get_team_repository),
    channel_repo = Depends(get_channel_repository),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_admin"):
        team = team_repo.get_by_id(target_name)
        if team:
            verify_team_access(team.name, current_user)
        else:
            channel = channel_repo.get_by_id(target_name)
            if channel:
                verify_team_access(channel.team_name, current_user)
            else:
                raise HTTPException(status_code=403, detail="You do not have access to this resource")

    db_trends = burnout_repo.get_trends(
        target_id=target_name, 
        start_date=start_date, 
        end_date=end_date
    )
    return [map_trend_to_historical_dto(trend) for trend in db_trends]