from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class MBIScores(BaseModel):
    exhaustion: float    
    cynicism: float       
    inefficacy: float    
    burnout_index: float 

class ContextMetrics(BaseModel):
    avg_overtime: float = 1.0
    avg_density: float = 0.0
    avg_latency: float = 0.0

class WBIScores(BaseModel):
    wbi: float
    wbi_e: float
    wbi_c: float
    wbi_i: float

class User(BaseModel):
    email: str = Field(alias="_id")
    name: str   
    role: Literal["admin", "employee"]
    managed_teams: List[str] = []
    teams: List[str] = []

class Team(BaseModel):
    name: str = Field(alias="_id")
    managers: List[str] = []
    visibility: Literal["public", "private", "org-wide"] 
    members: List[str] = []
    channels: List[str] = []
    burnout_mean: Optional[MBIScores] = None
    context_metrics: Optional[ContextMetrics] = None
    wbi_scores: Optional[WBIScores] = None

class Channel(BaseModel):
    id: str = Field(alias="_id")
    name: str 
    team_name: str
    visibility: Literal["public", "private", "shared"]
    channel_type: Literal["chat", "post"] 
    members: List[str] = []
    burnout_mean: Optional[MBIScores] = None
    context_metrics: Optional[ContextMetrics] = None
    wbi_scores: Optional[WBIScores] = None

class ConversationSession(BaseModel):
    id: str = Field(alias="_id")  
    channelId: str
    teamId: str
    startTime: str  
    endTime: str
    messageCount: int = 0
    sessionScores: Optional[MBIScores] = None
    wbi_scores: Optional[WBIScores] = None
    overtime_factor: float = 1.0
    density: float = 0.0
    latency: float = 0.0

    class Config:
        populate_by_name = True

class Message(BaseModel):
    id: str = Field(alias="_id")
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
    context: Optional[ContextMetrics] = None
    wbi: Optional[WBIScores] = None
    type: str

class Notification(BaseModel):
    id: str = Field(alias="_id")
    title: str
    message: str
    date: str
    target_team: Optional[str] = None
    read_by: List[str] = []