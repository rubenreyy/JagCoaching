import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body  # Added Path and Body


from database.cloud_db_controller import CloudDBController
from dependencies.auth import (
    CloudDBController, 
    get_current_active_user, 
    get_current_user, 
    oauth2_scheme, 
    get_current_active_user,
    get_user_sessions,          #  Phase 4
    terminate_session,          #  Phase 4
    verify_password,
    get_password_hash
)

from models.user_models import  UserCreate, UserUpdate, UserInDB, UserResponse, User , UserInDB
from dependencies.auth import get_password_hash
from dotenv import load_dotenv
from datetime import datetime
from bson.objectid import ObjectId



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
def get_profile(current_user: Annotated[dict, Depends(get_current_active_user)]):
    """Returns the profile data for the currently logged in user."""
    return {
        "status": "success",
        "user": {
            "username": current_user["username"],
            "email": current_user["email"],
            "is_active": current_user["is_active"],
            # "name": current_user["name"],
            # "created_at": current_user["created_at"],
            # "last_login": current_user["last_login"],
            # "preferences": current_user.get("preferences", {})
        }
    }

# Phase 4: List all sessions
@router.get("/sessions", response_description="List all active sessions for the current user")
async def list_user_sessions(current_user: dict = Depends(get_current_user)):
    """Returns all active sessions for the current user."""
    try:
        user_id = str(current_user["_id"])
        sessions = get_user_sessions(user_id)
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

# Phase 4: Terminate a session
@router.delete("/sessions/{session_id}", response_description="Terminate a session")
async def terminate_user_session(
    session_id: str = Path(..., description="Session ID to terminate"),
    current_user: dict = Depends(get_current_user)
):
    """Terminates a specific session for the current user."""
    try:
        result = terminate_session(session_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found or already terminated.")
        return {"status": "success", "message": f"Session {session_id} terminated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to terminate session: {str(e)}")

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

# Add this endpoint for password change with cascade revocation
@router.post("/change-password", response_description="Change user password and revoke all tokens")
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = str(current_user["_id"])
        
        # Verify current password
        if not verify_password(current_password, current_user.get("password", "")):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update password in database
        DB_CONNECTION.update_document(
            "JagCoaching", 
            "users", 
            {"_id": ObjectId(user_id)}, 
            {"password": hashed_password, "updated_at": datetime.now()}
        )
        
        # Cascade revocation - revoke all refresh tokens
        tokens_revoked = DB_CONNECTION.revoke_all_user_tokens(
            "JagCoaching", 
            user_id, 
            reason="password_change"
        )
        
        return {
            "status": "success", 
            "message": "Password changed successfully. All sessions have been terminated.",
            "tokens_revoked": tokens_revoked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

# Add this endpoint for session analytics
@router.get("/sessions/analytics", response_description="Get detailed session analytics")
async def get_session_analytics(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        analytics = DB_CONNECTION.get_user_session_analytics("JagCoaching", user_id)
        
        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session analytics: {str(e)}")