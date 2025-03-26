from datetime import datetime, timedelta, timezone
import os

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt
bcrypt.__about__ = bcrypt # some bug with passlib and bcrypt
from passlib.context import CryptContext
from dotenv import load_dotenv
from database.cloud_db_controller import CloudDBController
from models.user_models import TokenData, UserLogin, UserResponse, User



# Load environment variables
load_dotenv("./.env.development")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY","8aff34e1-d330-4eb8-b4be-5d35f5885451")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token",auto_error=False)


router = APIRouter()

DB_CONNECTION = CloudDBController()




def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password):
    """ Hash the given password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Create an access token with the given data and expiration time."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """ Get the current user from the given token."""
    print("getting user: ")
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials(user null)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            print("username is none")
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError as exc:
        print("jwt error")
        raise credentials_exception from exc
    user = get_user(db=DB_CONNECTION, username=token_data.username)

    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    """ Get the current active user."""
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


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

def authenticate_user(db: CloudDBController, email: str, password: str):
    try:
        user = db.find_document("JagCoaching", "users", {"email": email})
        if not user:
            print(f"User not found: {email}")
            return False
            
        print(f"Found user document: {user}")
        
        if not verify_password(password, user.get('password', '')):
            print("Password verification failed")
            return False
            
        return user
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False