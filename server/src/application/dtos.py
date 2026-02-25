from pydantic import BaseModel
from typing import List, Optional

class AuthStatusDTO(BaseModel):
    in_org: bool
    is_admin: bool
    is_owner: bool
    managed_teams: List[str] = []  
    auth_message: Optional[str] = None  