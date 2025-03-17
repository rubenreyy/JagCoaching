from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict

class UserBase(BaseModel):
    """Base user model with common attributes"""
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class UserCreate(UserBase):
    """Model for user creation requests"""
    password: str

class UserInDB(UserBase):
    """Model for user stored in database"""
    id: str
    hashed_password: str
    videos: List[str] = []
    preferences: Dict[str, str] = {}
    last_login: Optional[datetime] = None

class User(UserBase):
    """Model for user responses (no password)"""
    id: str

class UserUpdate(BaseModel):
    """Model for user update requests"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, str]] = None