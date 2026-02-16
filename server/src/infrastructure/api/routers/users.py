from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Retrieves the profile information of the currently authenticated user to determine frontend permissions.
@router.get("/me")
def get_my_user_info(current_user = Depends(get_current_user)):
    return {
        "username": current_user["_id"],
        "role": current_user["role"],
        "teams": current_user.get("teams", []),
        "email": current_user.get("email", "")
    }