from datetime import datetime, timedelta
import os
from typing import Optional
from fastapi import Depends, HTTPException, status , APIRouter
from fastapi.security import OAuth2PasswordBearer 
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from database.cloud_db_controller import CloudDBController
from models.user_models import UserLogin, UserResponse as User



# Load environment variables
load_dotenv("./src/backend/.env.development")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


router = APIRouter()





def verify_password(plain_password, hashed_password):
    """ Verify the given password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """ Hash the given password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Create an access token with the given data and expiration time."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """ Get the current user from the given token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    return User(username=username)


def get_user(db: CloudDBController, username: str):
    """ Get the user from the database."""
    db.connect()
    user = db.find_document(db_name="JagCoaching", collection_name="users", filter_dict={"username": username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def authenticate_user(db: CloudDBController, username: str, password: str):
    """ Authenticate the user by verifying the current user from the token."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user