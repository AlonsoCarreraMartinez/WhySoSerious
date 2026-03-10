from pydantic import BaseModel, Field
from typing import List, Optional

class MBIScores(BaseModel):
    exhaustion: float    # Emotional Exhaustion. 
    cynicism: float      # Cynicism, Depersonalization. 
    inefficacy: float    # Professional Inefficacy, Technical Block.
    burnout_index: float # Global burnout index.

class User(BaseModel):
    username: str = Field(alias="_id")
    name: str   
    email: str  
    role: str   # admin, manager, employee
    teams: List[str] = []

class Team(BaseModel):
    name: str = Field(alias="_id")
    manager: str
    visibility: str # public, private, org-wide.
    members: List[str] = []
    channels: List[str] = []
    description: Optional[str] = None
    burnout_mean: Optional[MBIScores] = None

class Channel(BaseModel):
    id: str = Field(alias="_id")
    name: str 
    team_name: str
    visibility: str # public, private, shared.
    channel_type: str # chat, posts.
    members: List[str] = []
    description: Optional[str] = None
    burnout_mean: Optional[MBIScores] = None

class ConversationSession(BaseModel):
    id: str = Field(alias="_id")  
    channelId: str
    teamId: str
    startTime: str  
    endTime: str
    messageCount: int = 0
    sessionScores: Optional[MBIScores] = None

class Message(BaseModel):
    externalId: str = Field(alias="_id")
    content: Optional[str] = None
    timestamp: str 
    teamId: Optional[str] = None      
    teamName: Optional[str] = None    
    channelId: Optional[str] = None   
    channelName: Optional[str] = None 
    sessionId: Optional[str] = None
    parentId: Optional[str] = None 
    analyzed: bool = False

    class Config:
        populate_by_name = True

class HealthTrend(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    targetId: str  
    date: str      
    score: MBIScores
    type: str