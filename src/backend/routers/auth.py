import os
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm
from models.user_models import  UserCreate, UserInDB, UserLogin , Token
from dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, get_current_user , create_access_token, get_password_hash
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
    # Initialize the database controller
    DB_CONNECTION.connect()
    
    print(DB_CONNECTION.get_database("JagCoaching"))
    # Check if user already exists
    existing_user = DB_CONNECTION.find_document(
        "JagCoaching",
        "users",
        {"email": form.email}
    )

    # If user already exists, return error
    if existing_user:
        return {"status": "error", "message": "User with this email already exists"}

    # Create new user document
    user_document = UserCreate(
        email=form.email,
        username=form.email,
        password=get_password_hash(form.password)
    ).model_dump()

    # Add user to the database
    result = DB_CONNECTION.add_document("JagCoaching", "users", user_document)

    # Check if user was successfully added
    if not result.acknowledged:
        return {"status": "error", "message": "Failed to create user"}
    print(result)
    # Close the database connection
    DB_CONNECTION.client.close()
    return {"status": "success", "message": "Registration successful!"}



@router.post("/auth/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Get access token for user login """
    print(form_data.username)
    # Initialize the database controller
    DB_CONNECTION.connect()
    user = authenticate_user(DB_CONNECTION, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # create token if everything else passes
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # close db connection
    DB_CONNECTION.client.close()
    return Token(access_token=access_token, token_type="bearer")



# TODO: Make Logout Function 
# Logout endpoint
@router.post("/api/logout/")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    print(current_user)
    return {"status": "success", "message": "Logout successful!"}


