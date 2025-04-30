import os
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request  # Phase 4: Request added
from fastapi.security import OAuth2PasswordRequestForm
from models.user_models import UserCreate, UserInDB, UserLogin, Token
from models.schemas import RefreshRequest, BlacklistRequest  # Phase 3
from dependencies.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
    create_refresh_token,
    hash_refresh_token,
    save_refresh_token_to_db,
    create_user_session,               # Phase 4
    terminate_all_user_sessions,       # Phase 4
    oauth2_scheme,                     # Added for token dependency
    record_failed_attempt,             # Added for rate limiting
    detect_suspicious_activity         # Added for suspicious activity detection
)
from database.cloud_db_controller import CloudDBController
from dotenv import load_dotenv
from jose import jwt  # Using jose instead of jwt

load_dotenv("./.env.development")

router = APIRouter(
    prefix="/api",
    tags=["auth"],
    responses={404: {"description": "Not found"}, 422: {"description": "Validation Error"}, 401: {"description": "Unauthorized"}},
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))
DB_CONNECTION = CloudDBController()

@router.post("/register", response_model=dict)
async def register(form: UserLogin):
    """ Register a new user account """
    try:
        # Initialize the database controller
        DB_CONNECTION.connect()
        
        # Check if user already exists
        existing_user = DB_CONNECTION.find_document(
            "JagCoaching",
            "users",
            {"email": form.email}
        )

        # If user already exists, return error
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        # Create new user document
        hashed_password = get_password_hash(form.password)
        user_document = {
            "username": form.email,  # Using email as username
            "email": form.email,
            "password": hashed_password,  # Store the hashed password
            "is_active": True,
            "created_at": datetime.now()
        }

        # Add user to the database
        result = DB_CONNECTION.add_document("JagCoaching", "users", user_document)

        # Check if user was successfully added
        if not result.acknowledged:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )

        return {"status": "success", "message": "Registration successful!"}
    
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    finally:
        # Close the database connection
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()



@router.post("/auth/token/", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        print(f"Login attempt for user: {form_data.username}")
        DB_CONNECTION.connect()
        user = DB_CONNECTION.find_document("JagCoaching", "users", {"email": form_data.username})

        if not user or not verify_password(form_data.password, user.get('password', '')):
            # Record failed login attempt for rate limiting
            ip_address = request.client.host if request.client else "unknown"
            record_failed_attempt(ip_address)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token()
        save_refresh_token_to_db(user_id=str(user["_id"]), refresh_token=refresh_token)

        # Enhanced session tracking
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent")
        device_info = {"user_agent": user_agent}
        
        # Create user session - fixed to match the function signature
        session_id = DB_CONNECTION.create_user_session(
            "JagCoaching", 
            str(user["_id"]), 
            ip_address, 
            device_info
        )
        
        # Check for suspicious activity
        detect_suspicious_activity(str(user["_id"]), ip_address, user_agent)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "session_id": session_id
        }

    except Exception as e:
        print(f"Login error: {str(e)}")
        raise
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()


@router.post("/auth/token/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest = Body(...)):
    """Refresh an expired access token using a valid refresh token"""
    try:
        DB_CONNECTION.connect()
        token_hash = hash_refresh_token(request.refresh_token)
        stored = DB_CONNECTION.get_refresh_token("JagCoaching", token_hash)

        if not stored or stored.get("expires_at") < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        user_id = stored["user_id"]
        DB_CONNECTION.delete_refresh_token("JagCoaching", token_hash)

        new_refresh_token = create_refresh_token()
        save_refresh_token_to_db(user_id=user_id, refresh_token=new_refresh_token)

        access_token = create_access_token(data={"sub": user_id})

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        print(f"Refresh token error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Logout and revoke the current token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp)
        DB_CONNECTION.revoke_token("JagCoaching", token=token, expires_at=expires_at, reason="user_logout")

        # Phase 4: End all active sessions for the user
        terminate_all_user_sessions(str(current_user["_id"]))

        return {"status": "success", "message": "Logout successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


# Phase 3: Admin route for manual blacklisting
@router.post("/auth/token/blacklist")
async def blacklist_token(request: BlacklistRequest = Body(...)):
    """Blacklist a token for security purposes"""
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp)
        DB_CONNECTION.blacklist_token("JagCoaching", token=request.token, expires_at=expires_at, reason=request.reason)
        return {"status": "success", "message": "Token has been blacklisted."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token already expired.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to blacklist token: {str(e)}")


