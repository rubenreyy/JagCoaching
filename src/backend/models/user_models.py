from datetime import datetime
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

# -- INFO: Models for user authentication and management -- #


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# Base user model with shared attributes
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=15)
    email: EmailStr = Field(...)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class UserCreate(User):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
    }


class UserInDB(User):
    password: str
    videos: List[str] = Field(default=[])
    preferences: Dict[str, str] = Field(default_factory=dict)
    last_login: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class UserResponse(User):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, str]] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


# Token model for authentication
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


# Test user data for development
test_user = {
    "username": "jagcoaching",
    "email": "jagcoaching@example.com",
    "password": "securepassword"
}
