from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class UserResponse(UserBase):
    id: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les tokens d'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Schémas pour les objets trouvés
class FoundItemBase(BaseModel):
    description: str
    found_date: str
    found_time: str
    location: str
    content_info: Optional[str] = None

class FoundItemCreate(FoundItemBase):
    pass

class FoundItemUpdate(BaseModel):
    description: Optional[str] = None
    found_date: Optional[str] = None
    found_time: Optional[str] = None
    location: Optional[str] = None
    content_info: Optional[str] = None

class FoundItemResponse(FoundItemBase):
    id: str
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    created_at: datetime
    possible_matches: List[str] = []
    
    class Config:
        from_attributes = True

# Schémas pour les objets perdus
class LostItemBase(BaseModel):
    description: str
    lost_date: str
    lost_time: str
    location: str
    content_info: Optional[str] = None

class LostItemCreate(LostItemBase):
    pass

class LostItemUpdate(BaseModel):
    description: Optional[str] = None
    lost_date: Optional[str] = None
    lost_time: Optional[str] = None
    location: Optional[str] = None
    content_info: Optional[str] = None

class LostItemResponse(LostItemBase):
    id: str
    created_at: datetime
    possible_matches: List[str] = []
    
    class Config:
        from_attributes = True

# Schéma pour les réponses de base
class MessageResponse(BaseModel):
    detail: str
