from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    name: str
    username: str
    email: str
    website: str
    companyName: str

class UpstreamUserData(BaseModel):
    id: int
    name: str
    username: str
    email: str
    website: str
    company: dict
    
    class Config:
        from_attributes = True

