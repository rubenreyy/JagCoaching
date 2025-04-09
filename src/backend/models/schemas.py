# Updated April 1 updated with token refresh schemas

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class UserPublic(UserBase):
    id: str
    created_at: datetime

# Auth & Token Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

# Phase 3: Blacklist Token Request Model
class BlacklistRequest(BaseModel):
    token: str
    reason: Optional[str] = "manual_blacklist"

# Session Tracking 
class TokenInfo(BaseModel):
    user_id: str
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None

# Phase 4: Session Management Models
class SessionCreate(BaseModel):
    user_id: str
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None

class SessionTerminateRequest(BaseModel):
    session_id: str
