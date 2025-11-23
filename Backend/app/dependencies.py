from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import decode_token
from app.database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload["sub"]
    user = db.users.find_one({"_id": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["username"] = user["_id"]
    return user
