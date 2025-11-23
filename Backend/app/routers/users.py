from fastapi import APIRouter
from app.database import db
from app.models import User
from app.auth import hash_password
from fastapi import Depends, HTTPException
from app.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Create a new user in the database.
@router.post("/create")
def create_user(user: User):
    db.users.insert_one({
        "_id": user.username,
        "role": user.role,
        "teams": user.teams,
        "password": hash_password(user.password)
    })
    return {"message": "User created", "user": user.username}

# Endpoint protected
@router.get("/admin-only")
def admin_only(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return {"message": "Welcome admin!"}