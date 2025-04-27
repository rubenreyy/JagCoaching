from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from bson import ObjectId

# -- INFO: Models for user authentication and management -- #


# Define PyObjectId for MongoDB ObjectId handling
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}

# Define base model for common attributes


class User(BaseModel):
    """Base user model with common attributes"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=15)
    email: EmailStr = Field(...)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(User):
    """Model for user creation requests"""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Model for user login credentials"""
    email: EmailStr
    password: str = Field(..., min_length=5)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class UserInDB(User):
    """Model for user in database"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    password: str  # Changed from hashed_password to password to match DB
    videos: List[str] = Field(default=[])
    preferences: Dict[str, str] = Field(default_factory=dict)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(User):
    """Model for user responses (no password)"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserUpdate(BaseModel):
    """Model for user update requests"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, str]] = None

    class Config:
        arbitrary_types_allowed = True


# Define token models for authentication
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Test user data for account page
test_user = {
    "username": "jagcoaching",
    "email": "jagcoaching@example.com",
    "password": "securepassword"
}
