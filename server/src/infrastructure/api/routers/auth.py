from fastapi import APIRouter, Depends
from application.dtos import AuthStatusDTO, LoginRequestDTO
from application.services.auth_service import AuthService
from infrastructure.api.dependencies import get_auth_service
from infrastructure.api.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/verify", response_model=AuthStatusDTO)
async def verify_user_role(
    request: LoginRequestDTO,
    auth_service: AuthService = Depends(get_auth_service)
):
    status = auth_service.validate_user_access(request.email)
    
    if status.in_org and (status.is_admin or status.is_owner):
        token_payload = {
            "email": request.email,
            "is_admin": status.is_admin,
            "managed_teams": status.managed_teams
        }
        status.token = create_access_token(token_payload)
        
    return status