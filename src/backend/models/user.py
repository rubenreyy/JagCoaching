from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from bson import ObjectId
from pymongo import MongoClient


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

class UserBase(BaseModel):
    """Base user model with common attributes"""
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(UserBase):
    """Model for user creation requests"""
    password: str

class UserLogin(BaseModel):
    """Model for user login credentials"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
class UserInDB(UserBase):
    """Model for user stored in database"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    videos: List[str] = Field(default=[])
    preferences: Dict[str, str] = Field(default_factory=dict)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
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


# Test user data for account page
test_user = {
    "username": "jagcoaching",
    "email": "jagcoaching@example.com",
    "password": "securepassword"
}


