from datetime import datetime, timedelta, timezone
import os

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt
bcrypt.__about__ = bcrypt  # some bug with passlib and bcrypt
from passlib.context import CryptContext
from dotenv import load_dotenv
from database.cloud_db_controller import CloudDBController
from models.user_models import TokenData, UserLogin, UserResponse, User
from config import settings
import secrets
import hashlib
from uuid import uuid4  # 🔒 Added for session IDs

# Load environment variables
load_dotenv("./.env.development")

# Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

router = APIRouter()
DB_CONNECTION = CloudDBController()

# Angelo Updated April 1: Utility Functions
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
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Angelo Updated April 1 // Phase 1: Refresh Token Helpers
def create_refresh_token():
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def save_refresh_token_to_db(user_id: str, refresh_token: str, device_info: Optional[dict] = None):
    token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    DB_CONNECTION.save_refresh_token("JagCoaching", {
        "user_id": user_id,
        "token_hash": token_hash,
        "expires_at": expires_at,
        "device_info": device_info,
        "created_at": datetime.utcnow()
    })

# Angelo Added April 8 // Phase 4: Session Helpers
def create_user_session(user_id: str, ip_address: Optional[str] = None, device_info: Optional[dict] = None):
    session_data = {
        "session_id": str(uuid4()),
        "user_id": user_id,
        "ip_address": ip_address,
        "device_info": device_info,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    DB_CONNECTION.create_session("JagCoaching", session_data)
    return session_data["session_id"]

def get_user_sessions(user_id: str):
    return DB_CONNECTION.get_sessions_by_user("JagCoaching", user_id)

def terminate_session(session_id: str):
    return DB_CONNECTION.terminate_session("JagCoaching", session_id)

def terminate_all_user_sessions(user_id: str):
    return DB_CONNECTION.terminate_all_sessions("JagCoaching", user_id)

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
        # Angelo Updated April 8 // Phase 2 + 3: Check for revoked OR blacklisted token
        revoked_entry = DB_CONNECTION.is_token_revoked("JagCoaching", token)
        if revoked_entry:
            reason = revoked_entry.get("reason", "revoked")
            token_type = revoked_entry.get("type", "revoked")
            if reason == "blacklisted" or token_type == "blacklist":
                raise HTTPException(status_code=403, detail="Token blacklisted. Access denied.")
            raise HTTPException(status_code=401, detail="Token has been revoked")

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
