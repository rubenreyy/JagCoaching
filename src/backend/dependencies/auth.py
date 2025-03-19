from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from models.user import User

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None





def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")

        if username is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception

    # In a real application, you would fetch the user from your database here
    # This is just a placeholder implementation
    user = User(
        id=token_data.user_id,
        username=token_data.username,
        email=f"{token_data.username}@example.com"
    )

    if user is None:
        raise credentials_exception

    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure the user is active"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_password_hash(password: str):
    """Generate a password hash"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)