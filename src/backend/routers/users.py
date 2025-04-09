import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path  # Added Path for session ID routing

from database.cloud_db_controller import CloudDBController
from dependencies.auth import (
    CloudDBController,
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
    get_user_sessions,         
    terminate_session           
)

from models.user_models import UserCreate, UserUpdate, UserInDB, UserResponse, User
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
def get_profile(token: Annotated[str, Depends(get_current_active_user)]):
    """Returns the profile data for the currently logged in user."""
    print(token)
    user = get_current_active_user(token)

    return {
        "status": "success",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
        }
    }

# List active sessions for the current user
@router.get("/sessions", response_description="List all active sessions for the current user")
async def list_user_sessions(current_user: dict = Depends(get_current_user)):
    """
    Returns all active sessions (IP, device info, timestamps) for the current user.
    """
    try:
        user_id = str(current_user["_id"])
        sessions = get_user_sessions(user_id)
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

# Terminate a specific session by session ID
@router.delete("/sessions/{session_id}", response_description="Terminate a session")
async def terminate_user_session(
    session_id: str = Path(..., description="Session ID to terminate"),
    current_user: dict = Depends(get_current_user)
):
    """
    Terminates a specific session by session ID for the current user.
    """
    try:
        result = terminate_session(session_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found or already terminated.")
        return {"status": "success", "message": f"Session {session_id} terminated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to terminate session: {str(e)}")
