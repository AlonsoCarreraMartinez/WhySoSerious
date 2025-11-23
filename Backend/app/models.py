from pydantic import BaseModel
from typing import List


class User(BaseModel):
    username: str
    role: str   # "admin", "manager", "user"
    teams: List[str]
    password: str


class Team(BaseModel):
    name: str
    manager: str
    members: List[str]
