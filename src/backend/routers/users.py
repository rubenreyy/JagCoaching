import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId

from database.cloud_db_controller import CloudDBController
from dependencies.auth import CloudDBController, get_current_user
from models.user_models import UserInDB as User
from models.user_models import  UserCreate, UserUpdate, UserInDB
from dependencies.auth import get_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.env.development")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

DB_CONNECTION = CloudDBController()

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Get profile data for the logged in user
@router.get("/profile/", response_description="Get profile data for the logged in user")
def get_profile(token: OAuth2PasswordBearer = Depends(get_current_user)):
    """Returns the profile data for the currently logged in user."""

    # decrypts key and gets user
    user =  get_current_user(token)
    DB_CONNECTION.connect()

    # gets user in db
    user_in_db = DB_CONNECTION.find_document("JagCoaching", "users", {"email": user.email})
    DB_CONNECTION.client.close()
    

    if user_in_db is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "user": {
            "username": user_in_db["username"],
            "email": user_in_db["email"],
            "name": user_in_db["name"],
            "created_at": user_in_db["created_at"],
            "last_login": user_in_db["last_login"],
            "preferences": user.get("preferences", {})
        }
    }

# @router.get("/profile/{user_id}", response_model=User)
# async def read_user(user_id: str, db = Depends(get_db)):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
        
#     user = await db["users"].find_one({"_id": ObjectId(user_id)})
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user


# TODO: Add changes to user profile Implementation
# @router.put("/{user_id}", response_model=User)
# async def update_user_info(user_id: str, user: UserUpdate, db = Depends(get_db)):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
    
#     # Get only the fields that are set
#     update_data = {k: v for k, v in user.dict(exclude_unset=True).items()}
    
#     # Hash new password if provided
#     if "password" in update_data:
#         from dependencies.auth import get_password_hash
#         update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
#     # Add updated timestamp
#     from datetime import datetime
#     update_data["updated_at"] = datetime.now()
    
#     # Update user in database
#     result = await db["users"].update_one(
#         {"_id": ObjectId(user_id)},
#         {"$set": update_data}
#     )
    
#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="User not found")
        
#     # Return updated user
#     updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
#     return updated_user

# TODO: Delete user Implementation
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_user(user_id: str, db = Depends(get_db)):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID format")
        
#     result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="User not found")
        
#     return {"message": "User deleted successfully"}