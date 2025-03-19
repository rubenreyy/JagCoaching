from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from bson import ObjectId
from database.database import get_db
from models.user import User, UserCreate, UserUpdate, UserInDB, PyObjectId
from dependencies.auth import get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db = Depends(get_db)):
    # Check if user with this email already exists
    if await db["users"].find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password and prepare user document
    # from ..core.security import get_password_hash
    user_data = user.dict()
    hashed_password = get_password_hash(user_data.pop("password"))
    
    # Create user document for MongoDB
    user_in_db = UserInDB(**user_data, hashed_password=hashed_password)
    
    # Insert into MongoDB
    result = await db["users"].insert_one(user_in_db.dict(by_alias=True))
    
    # Retrieve and return the created user
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return created_user

@router.get("/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    users = await db["users"].find().skip(skip).limit(limit).to_list(length=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user_info(user_id: str, user: UserUpdate, db = Depends(get_db)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Get only the fields that are set
    update_data = {k: v for k, v in user.dict(exclude_unset=True).items()}
    
    # Hash new password if provided
    if "password" in update_data:
        from dependencies.auth import get_password_hash
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Add updated timestamp
    from datetime import datetime
    update_data["updated_at"] = datetime.now()
    
    # Update user in database
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Return updated user
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": "User deleted successfully"}