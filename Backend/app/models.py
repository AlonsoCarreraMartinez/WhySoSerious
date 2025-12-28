from pydantic import BaseModel, Field
from typing import List, Optional


class User(BaseModel):
    username: str = Field(alias="_id")
    name: str   
    email: str  
    role: str   # "admin", "manager", "user"
    teams: List[str]
    password: str


class Team(BaseModel):
    name: str = Field(alias="_id")
    manager: str
    members: List[str]


class BertScores(BaseModel):
    politeness: float
    sarcasm: float
    toxicity: float


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