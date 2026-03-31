from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from application.dtos import HistoricalDataPointDTO
from infrastructure.api.dependencies import get_burnout_repository
from infrastructure.api.mappers import map_trend_to_historical_dto

router = APIRouter(prefix="/burnout", tags=["Burnout"])

@router.get("/historical/{target_name}", response_model=List[HistoricalDataPointDTO])
async def get_historical_data(
    target_name: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    burnout_repo = Depends(get_burnout_repository)
):
    db_trends = burnout_repo.get_trends(
        target_id=target_name, 
        start_date=start_date, 
        end_date=end_date
    )
    return [map_trend_to_historical_dto(trend) for trend in db_trends]