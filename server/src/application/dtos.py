from pydantic import BaseModel
from typing import List, Optional

class AuthStatusDTO(BaseModel):
    in_org: bool
    is_admin: bool
    is_owner: bool
    managed_teams: List[str] = []  
    auth_message: Optional[str] = None  

class LoginRequestDTO(BaseModel):
    email: str

class TeamDashboardResponseDTO(BaseModel):
    id: str
    name: str
    visibility: str
    memberCount: int
    burnoutScore: int
    burnoutLevel: str 
    exhaustion: int
    cynicism: int
    inefficacy: int

class ChannelDashboardResponseDTO(BaseModel):
    id: str
    teamId: str
    name: str
    visibility: str
    memberCount: int
    burnoutScore: int
    burnoutLevel: str
    exhaustion: int
    cynicism: int
    inefficacy: int

class HistoricalDataPointDTO(BaseModel):
    date: str
    score: int
    exhaustion: int
    cynicism: int
    inefficacy: int

class MemberResponseDTO(BaseModel):
    id: str
    name: str
    email: str
    role: str