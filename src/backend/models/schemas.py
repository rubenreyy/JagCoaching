from pydantic import BaseModel
from typing import List, Optional

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
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


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
