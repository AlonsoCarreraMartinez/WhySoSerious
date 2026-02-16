from fastapi import APIRouter, HTTPException
from app.database import db
from app.auth import verify_password, create_access_token
from app.models import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

# Authenticates the user credentials and issues a JWT Token for session management.
@router.post("/login")
def login(credentials: LoginRequest):
    user = db.users.find_one({"_id": credentials.username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"sub": user["_id"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}
