from fastapi import APIRouter
from app.database import db
from app.models import User
from app.auth import hash_password
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Create a new user in the database.
@router.post("/create")
def create_user(user: User):
    
    if db.users.find_one({"_id": user.username}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    db.users.insert_one({
        "_id": user.username,
        "username": user.username,
        "name": getattr(user, "name", "Unknown"), 
        "email": getattr(user, "email", user.username),
        "role": user.role,
        "teams": user.teams,
        "password": hash_password(user.password)
    })
    
    return {"message": "User created", "user": user.username}


@router.get("/admin-only")
def admin_only(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return {"message": "Welcome admin!"}