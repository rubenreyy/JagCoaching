from pydantic import BaseModel
from typing import List, Optional

#
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int

    class Config:
        from_attributes = True

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