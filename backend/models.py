from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class FoundItem(BaseModel):
    id: Optional[str] = None
    description: str
    found_date: datetime
    found_time: str
    location: str
    content_info: str
    image_filename: str
    created_at: Optional[datetime] = None
    possible_matches: List[str] = []


class LostItem(BaseModel):
    id: Optional[str] = None
    description: str
    lost_date: datetime
    lost_time: str
    location: str
    content_info: str
    created_at: Optional[datetime] = None
    possible_matches: List[str] = []


class User(BaseModel):
    username: str
    password: str
