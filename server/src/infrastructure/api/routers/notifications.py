from fastapi import APIRouter, Depends, HTTPException
from typing import List
from application.dtos import NotificationResponseDTO, MarkReadRequestDTO
from infrastructure.api.dependencies import get_notification_repository, get_user_repository, get_team_repository
from infrastructure.api.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Manages the retrieval of alerts and system notifications for a specific user based on their role.
@router.get("/{email}", response_model=List[NotificationResponseDTO])
async def get_user_notifications(
    email: str,
    notification_repo = Depends(get_notification_repository),
    user_repo = Depends(get_user_repository),
    team_repo = Depends(get_team_repository),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_admin") and current_user.get("email") != email:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    db_user = user_repo.get_by_email(email)
    is_admin = db_user.role == "admin" if db_user else False
    
    managed_teams = team_repo.get_by_manager(email)
    managed_team_names = [t.name for t in managed_teams]

    db_notifs = notification_repo.get_for_user(is_admin, managed_team_names)
    
    results = []
    for n in db_notifs:
        results.append(NotificationResponseDTO(
            id=n.id,
            title=n.title,
            message=n.message,
            date=n.date,
            targetTeam=n.target_team,
            isRead=email in n.read_by
        ))
    return results

# Allows users to mark specific notifications as read to update the UI badge.
@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    request: MarkReadRequestDTO,
    notification_repo = Depends(get_notification_repository),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_admin") and current_user.get("email") != request.email:
        raise HTTPException(status_code=403, detail="Unauthorized access")
        
    notification_repo.mark_as_read(notification_id, request.email)
    return {"status": "success"}