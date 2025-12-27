from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    username: str
    name: str   
    email: str  
    role: str   # "admin", "manager", "user"
    teams: List[str]
    password: str


class Team(BaseModel):
    name: str
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
    platform: str
    analyzed: bool = False
    scores: Optional[BertScores] = None 

    class Config:
        populate_by_name = True