from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# models old temp


class FileName(BaseModel):
    file_name: str


class UploadResponse(BaseModel):
    filename: str
    status: str


# User schemas


class user(BaseModel):
    username: str
    email: str


class UserCreate(user):
    password: str


class User(user):
    id: int

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


# Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
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


# Video schemas
class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class Video(VideoBase):
    id: int

    class Config:
        from_attributes = True


# Feedback schemas
class Feedback(BaseModel):
    transcript: str
    sentiment: str
    filler_words: List[str]
    emotion: str
    keywords: List[str]
    pauses: List[str]
    wpm: float
    clarity: float


class FeedbackResponse(BaseModel):
    feedback: Feedback
