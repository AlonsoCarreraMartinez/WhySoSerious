from pydantic import BaseModel, Field
from typing import List, Optional


class User(BaseModel):
    username: str = Field(alias="_id")
    name: str   
    email: str  
    role: str   # "admin", "manager", "employee"
    teams: List[str]
    password: str

class BertScores(BaseModel):
    politeness: float
    sarcasm: float
    toxicity: float

class Channel(BaseModel):
    id: str = Field(alias="_id")
    name: str 
    team_name: str
    burnout_mean: Optional[BertScores] = None

class Team(BaseModel):
    name: str = Field(alias="_id")
    manager: str
    members: List[str]
    channels: List[str] = []
    burnout_mean: Optional[BertScores] = None


class MessageDB(BaseModel):
    externalId: str 
    content: str
    sender: str
    timestamp: str 
    teamId: Optional[str] = None      
    teamName: Optional[str] = None    
    channelId: Optional[str] = None   
    channelName: Optional[str] = None 
    analyzed: bool = False
    scores: Optional[BertScores] = None 

    class Config:
        populate_by_name = True