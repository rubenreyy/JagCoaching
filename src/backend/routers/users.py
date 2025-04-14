import os
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv

from database.cloud_db_controller import CloudDBController
from dependencies.auth import get_current_active_user
from models.user_models import UserInDB

# Logging setup
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("./.env.development")

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Router setup
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# DB instance
DB_CONNECTION = CloudDBController()


@router.get("/profile/", response_description="Get profile data for the logged in user")
def get_profile(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """Returns the profile data for the currently logged in user."""
    try:
        logger.info(f"Returning profile for user: {current_user.get('email')}")
        return {
            "status": "success",
            "user": {
                "username": current_user["username"],
                "email": current_user["email"],
                "is_active": current_user["is_active"],
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch user profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")
