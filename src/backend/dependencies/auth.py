from datetime import datetime, timedelta, timezone
import os
import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from passlib.context import CryptContext
from dotenv import load_dotenv

from database.cloud_db_controller import CloudDBController
from models.user_models import TokenData, UserLogin, UserResponse, User

# Setup logger
logger = logging.getLogger(__name__)

# Workaround for passlib + bcrypt import issue
bcrypt.__about__ = bcrypt

# Load environment variables
load_dotenv("./.env.development")

# Config values
SECRET_KEY = os.getenv("SECRET_KEY", "8aff34e1-d330-4eb8-b4be-5d35f5885451")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security tools
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

# Optional if you use routing from here
router = APIRouter()

# DB controller instance
DB_CONNECTION = CloudDBController()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed version."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash the given password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """Decode JWT and return current user document from DB."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (user null)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        logger.error("JWT decoding failed.")
        raise credentials_exception from exc

    user = get_user(db=DB_CONNECTION, username=token_data.username)
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """Ensure user is authenticated and active."""
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user(db: CloudDBController, username: str) -> dict:
    """Fetch user document from database by username."""
    db.connect()
    user = db.find_document(
        db_name="JagCoaching", collection_name="users", filter_dict={"username": username}
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def authenticate_user(db: CloudDBController, email: str, password: str) -> Optional[dict]:
    """Authenticate user by email and password."""
    try:
        user = db.find_document("JagCoaching", "users", {"email": email})
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        if not verify_password(password, user.get("password", "")):
            logger.warning("Password verification failed")
            return None

        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None
