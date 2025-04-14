import os
import logging
from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv

from models.user_models import UserLogin, UserInDB, Token
from dependencies.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
)
from database.cloud_db_controller import CloudDBController

# Load environment variables
load_dotenv("./.env.development")

# Logger setup
logger = logging.getLogger(__name__)

# Router
router = APIRouter(
    tags=["auth"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation Error"},
        401: {"description": "Unauthorized"}
    },
)

# Environment config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DB_CONNECTION = CloudDBController()

# --------------------------
# Register
# --------------------------

@router.post("/register", response_model=dict)
async def register(form: UserLogin):
    """Register a new user account"""
    try:
        DB_CONNECTION.connect()

        existing_user = DB_CONNECTION.find_document(
            "JagCoaching", "users", {"email": form.email}
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        hashed_password = get_password_hash(form.password)
        user_document = {
            "username": form.email,
            "email": form.email,
            "password": hashed_password,
            "is_active": True,
            "created_at": datetime.now()
        }

        result = DB_CONNECTION.add_document("JagCoaching", "users", user_document)

        if not result.acknowledged:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )

        return {"status": "success", "message": "Registration successful!"}

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

# --------------------------
# Login
# --------------------------

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Authenticate user and return JWT access token"""
    try:
        logger.info(f"Login attempt for: {form_data.username}")
        DB_CONNECTION.connect()

        user = DB_CONNECTION.find_document(
            "JagCoaching", "users", {"email": form_data.username}
        )

        if not user or not verify_password(form_data.password, user.get('password', '')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

# --------------------------
# Logout (stub)
# --------------------------

@router.post("/logout", response_model=dict)
async def logout(current_user: UserInDB = Depends(get_current_user)):
    """Logout endpoint — relies on client token removal."""
    logger.info(f"User logging out: {current_user.get('email')}")
    return {"status": "success", "message": "Logout successful!"}
