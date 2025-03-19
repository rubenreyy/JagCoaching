import typing 
from typing import List, Optional, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
import pymongo
from pymongo import MongoClient

# Define the PyObjectId class for handling MongoDB's ObjectId
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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    email: EmailStr = Field(...)
    full_name: str = Field(...)
    disabled: bool = Field(default=False)
    hashed_password: str = Field(...)
    roles: List[str] = Field(default=["user"])

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "disabled": False,
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "roles": ["user"]
            }
        }

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "password": "password123"
            }
        }

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    full_name: Optional[str]
    password: Optional[str]
    disabled: Optional[bool]
    roles: Optional[List[str]]

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "password": "password123",
                "disabled": False,
                "roles": ["user"]
            }
        }

class UserInDB(UserModel):
    hashed_password: str

class User(UserModel):
    def __init__(self, **data):
        super().__init__(**data)

    def get_roles(self) -> List[str]:
        return self.roles
    