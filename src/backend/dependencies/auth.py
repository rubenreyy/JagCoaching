from datetime import datetime, timedelta, timezone
import os
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, APIRouter, Request  # Added Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
bcrypt.__about__ = bcrypt # some bug with passlib and bcrypt
from passlib.context import CryptContext
from dotenv import load_dotenv
from database.cloud_db_controller import CloudDBController
from models.user_models import TokenData, UserLogin, UserResponse, User
import secrets
import hashlib
from uuid import uuid4  # Added for session IDs
import time  # Added for rate limiting
import logging
import json  # For logging

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("security.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv("./.env.development")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY","8aff34e1-d330-4eb8-b4be-5d35f5885451")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 14  # 2 weeks for refresh tokens

# Rate limiting configuration
MAX_FAILED_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 15 * 60  # 15 minutes in seconds
failed_attempts = {}  # IP -> {count: int, first_attempt: timestamp}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token",auto_error=False)


router = APIRouter()

DB_CONNECTION = CloudDBController()

# PHASE 4: MAX SESSION LIMIT
MAX_SESSIONS_PER_USER = 5


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
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Refresh Token Helpers
def create_refresh_token():
    """Create a secure refresh token"""
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str):
    """Hash a refresh token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def save_refresh_token_to_db(user_id: str, refresh_token: str, device_info: Optional[dict] = None):
    """Save a refresh token to the database"""
    token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    DB_CONNECTION.save_refresh_token("JagCoaching", {
        "user_id": user_id,
        "token_hash": token_hash,
        "expires_at": expires_at,
        "device_info": device_info,
        "created_at": datetime.utcnow()
    })

# Phase 4: Enforce Max Sessions Per User
def enforce_max_sessions(user_id: str):
    """Ensure user doesn't exceed maximum allowed sessions"""
    sessions = DB_CONNECTION.get_sessions_for_user("JagCoaching", user_id)
    if len(sessions) >= MAX_SESSIONS_PER_USER:
        sessions_sorted = sorted(sessions, key=lambda x: x.get("created_at"))
        for old_session in sessions_sorted[:len(sessions) - MAX_SESSIONS_PER_USER + 1]:
            DB_CONNECTION.delete_session("JagCoaching", old_session["session_id"])

# Phase 4: Enhanced Session Helpers
def create_user_session(user_id: str, ip_address: Optional[str] = None, device_info: Optional[dict] = None):
    """Create a new user session with tracking information"""
    enforce_max_sessions(user_id)  # enforce before session creation
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
    """Get all active sessions for a user"""
    return DB_CONNECTION.get_sessions_for_user("JagCoaching", user_id)

def terminate_session(session_id: str):
    """End a specific user session"""
    return DB_CONNECTION.delete_session("JagCoaching", session_id)

def terminate_all_user_sessions(user_id: str):
    """End all sessions for a specific user"""
    return DB_CONNECTION.delete_all_sessions_for_user("JagCoaching", user_id)


async def get_current_user(request: Request = None, token: str = Depends(oauth2_scheme)):
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get client info for security checks
    ip_address = "unknown"
    user_agent = None
    if request:
        if request.client:
            ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
    
    # Check if IP is rate limited
    if check_rate_limit(ip_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again later."
        )
    
    try:
        if token is None:
            raise credentials_exception
            
        # Check if token is revoked or blacklisted
        revoked_entry = DB_CONNECTION.is_token_revoked("JagCoaching", token)
        if revoked_entry:
            reason = revoked_entry.get("reason", "revoked")
            token_type = revoked_entry.get("type", "revoked")
            if reason == "blacklisted" or token_type == "blacklist":
                raise HTTPException(status_code=403, detail="Token blacklisted. Access denied.")
            raise HTTPException(status_code=401, detail="Token has been revoked")
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("username is none")
            record_failed_attempt(ip_address)
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        print("jwt error")
        record_failed_attempt(ip_address)
        raise credentials_exception from exc
    
    user = get_user(db=DB_CONNECTION, username=token_data.username)
    
    # Check for suspicious activity
    if user and request:
        detect_suspicious_activity(str(user["_id"]), ip_address, user_agent)
    
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

# Add this function for rate limiting
def check_rate_limit(ip_address: str) -> bool:
    """
    Check if the IP address has exceeded the rate limit for failed attempts.
    Returns True if rate limited, False otherwise.
    """
    current_time = time.time()
    
    # Clean up expired entries
    expired = [ip for ip, data in failed_attempts.items() 
               if current_time - data['first_attempt'] > RATE_LIMIT_WINDOW]
    for ip in expired:
        del failed_attempts[ip]
    
    # Check if IP is already rate limited
    if ip_address in failed_attempts:
        data = failed_attempts[ip_address]
        # If window has expired, reset the counter
        if current_time - data['first_attempt'] > RATE_LIMIT_WINDOW:
            failed_attempts[ip_address] = {'count': 1, 'first_attempt': current_time}
            return False
        # If too many attempts, rate limit
        if data['count'] >= MAX_FAILED_ATTEMPTS:
            return True
        # Otherwise increment the counter
        data['count'] += 1
        return False
    else:
        # First attempt from this IP
        failed_attempts[ip_address] = {'count': 1, 'first_attempt': current_time}
        return False

def record_failed_attempt(ip_address: str):
    """Record a failed token attempt for rate limiting"""
    current_time = time.time()
    if ip_address in failed_attempts:
        failed_attempts[ip_address]['count'] += 1
    else:
        failed_attempts[ip_address] = {'count': 1, 'first_attempt': current_time}
    
    # Log suspicious activity if multiple failures
    if failed_attempts[ip_address]['count'] >= 3:
        logger.warning(f"Multiple failed token attempts from IP: {ip_address}, " 
                      f"count: {failed_attempts[ip_address]['count']}")

# Add this function for suspicious activity detection
def detect_suspicious_activity(user_id: str, ip_address: str, user_agent: str = None):
    """
    Detect suspicious token usage patterns and log them.
    """
    # Get user's recent sessions
    recent_sessions = DB_CONNECTION.get_user_recent_sessions("JagCoaching", user_id, limit=5)
    
    suspicious = False
    reason = []
    
    # Check for unusual IP address
    known_ips = [session.get('ip_address') for session in recent_sessions 
                if session.get('ip_address')]
    
    if known_ips and ip_address not in known_ips:
        suspicious = True
        reason.append(f"New IP address: {ip_address}")
    
    # Check for unusual user agent if provided
    if user_agent:
        known_agents = []
        for session in recent_sessions:
            device_info = session.get('device_info', {})
            if device_info and 'user_agent' in device_info:
                known_agents.append(device_info['user_agent'])
        
        if known_agents and user_agent not in known_agents:
            suspicious = True
            reason.append(f"New user agent: {user_agent}")
    
    # Check for rapid location changes (would require GeoIP lookup)
    # This is a placeholder for more sophisticated checks
    
    # Log suspicious activity
    if suspicious:
        logger.warning(f"SUSPICIOUS TOKEN USAGE: User {user_id}, Reasons: {', '.join(reason)}")
        
        # Record the suspicious activity in the database
        DB_CONNECTION.record_security_event("JagCoaching", {
            "user_id": user_id,
            "event_type": "suspicious_token_usage",
            "ip_address": ip_address,
            "user_agent": user_agent,
            "reasons": reason,
            "timestamp": datetime.now()
        })
    
    return suspicious
