import os
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm
from models.user_models import  UserCreate, UserInDB, UserLogin , Token
from dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, get_current_user , create_access_token, get_password_hash, verify_password
from database.cloud_db_controller import CloudDBController
from dotenv import load_dotenv

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

@router.post("/register/")
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
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Get access token for user login"""
    try:
        print(f"Login attempt for user: {form_data.username}")
        
        # Initialize the database controller
        DB_CONNECTION.connect()
        
        # Find user by email
        user = DB_CONNECTION.find_document(
            "JagCoaching",
            "users",
            {"email": form_data.username}
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        print(f"Found user: {user}")
        
        # Verify password
        if not verify_password(form_data.password, user.get('password', '')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()



# TODO: Make Logout Function 
# Logout endpoint
@router.post("/api/logout/")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    print(current_user)
    return {"status": "success", "message": "Logout successful!"}


