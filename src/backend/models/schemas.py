from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


# File & Upload Schemas
class FileName(BaseModel):
    file_name: str


class UploadResponse(BaseModel):
    filename: str
    status: str


# -------------------------------
# User Schemas
# -------------------------------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True  # used to support ORM response models
    }


class UserInDB(User):
    hashed_password: str


# -------------------------------
# Authentication Schemas
# -------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# -------------------------------
# Video Schemas
# -------------------------------

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class Video(VideoBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# -------------------------------
# Feedback Schemas
# -------------------------------

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
