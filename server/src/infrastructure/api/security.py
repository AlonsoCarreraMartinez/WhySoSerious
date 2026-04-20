import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.config.settings import settings

security = HTTPBearer()

def create_access_token(data: dict):
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        return jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid, expired or missing token")

def verify_team_access(team_name: str, current_user: dict):
    if current_user.get("is_admin"):
        return True
    
    managed_teams = [team["name"] for team in current_user.get("managed_teams", [])]
    if team_name not in managed_teams:
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    
    return True