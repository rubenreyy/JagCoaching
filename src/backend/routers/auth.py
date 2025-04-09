import os
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request  # Added Request
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
    create_user_session,  # Phase 4
    terminate_all_user_sessions  # Phase 4
)
from database.cloud_db_controller import CloudDBController
from dotenv import load_dotenv
import jwt

load_dotenv("./.env.development")

router = APIRouter(
    prefix="/api",
    tags=["auth"],
    responses={404: {"description": "Not found"}, 422: {"description": "Validation Error"}, 401: {"description": "Unauthorized"}},
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DB_CONNECTION = CloudDBController()

@router.post("/register/")
async def register(form: UserLogin):
    try:
        DB_CONNECTION.connect()
        existing_user = DB_CONNECTION.find_document("JagCoaching", "users", {"email": form.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

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
            raise HTTPException(status_code=500, detail="Failed to create user")

        return {"status": "success", "message": "Registration successful!"}

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()


@router.post("/auth/token/", response_model=Token)
async def login_for_access_token(
    request: Request,  # For IP and headers
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        print(f"Login attempt for user: {form_data.username}")
        DB_CONNECTION.connect()
        user = DB_CONNECTION.find_document("JagCoaching", "users", {"email": form_data.username})

        if not user or not verify_password(form_data.password, user.get('password', '')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token()
        save_refresh_token_to_db(user_id=str(user["_id"]), refresh_token=refresh_token)

        # Phase 4: Create a session upon login
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        device_info = {"user_agent": user_agent}
        create_user_session(user_id=str(user["_id"]), ip_address=ip_address, device_info=device_info)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        print(f"Login error: {str(e)}")
        raise
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

@router.post("/auth/token/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest = Body(...)):
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

@router.post("/api/logout/")
async def logout(current_user: UserInDB = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp)
        DB_CONNECTION.revoke_token("JagCoaching", token=token, expires_at=expires_at, reason="user_logout")

        # Phase 4: End all user sessions on logout
        terminate_all_user_sessions(str(current_user.id))

        return {"status": "success", "message": "Logout successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

# Phase 3: Admin route to blacklist a token
@router.post("/auth/token/blacklist")
async def blacklist_token(request: BlacklistRequest = Body(...)):
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
