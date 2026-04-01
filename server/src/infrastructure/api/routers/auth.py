from fastapi import APIRouter, Depends
from application.dtos import AuthStatusDTO, LoginRequestDTO
from application.services.auth_service import AuthService
from infrastructure.api.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/verify", response_model=AuthStatusDTO)
async def verify_user_role(
    request: LoginRequestDTO,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.validate_user_access(request.email)