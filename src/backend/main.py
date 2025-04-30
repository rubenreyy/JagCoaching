# Include the project root directory in the Python path if testing this file only
# third-party imports

import sys
import os
if sys.path.count(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) == 0:
    sys.path.append(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
from config import settings
from routers import auth_router, videos_router, users_router, live_router, presentations
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Built-in imports
from contextlib import asynccontextmanager
from pathlib import Path

import dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Create logger instance
logger = logging.getLogger(__name__)

dotenv.load_dotenv("./env.development") # consolidated to one env folder

UPLOAD_DIR = settings.UPLOAD_FOLDER

# Startup and shutdown event handlers for fastapi
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create necessary directories on startup."""
    try:
        UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
        VIDEO_DIR = UPLOAD_DIR / "videos"
        AUDIO_DIR = VIDEO_DIR / "audio"
        
        for directory in [UPLOAD_DIR, VIDEO_DIR, AUDIO_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        yield
        
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error in lifespan: {str(e)}")
        raise

# Create a single FastAPI app instance
app = FastAPI(lifespan=lifespan)

# Include the routers in the main FastAPI application
app.include_router(users_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(videos_router, prefix="/api")
app.include_router(live_router.router, prefix="/api")
app.include_router(presentations.router, prefix="/api")

# Get allowed origins from environment or use defaults
# Update the origins to include both localhost and the ngrok URL
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Add wildcard for ngrok domains
ngrok_origins = ["https://*.ngrok-free.app", "https://*.ngrok.io"]

# Update the CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.ngrok-free.app",  
        "https://*.ngrok.io",      
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def index():
    return {"message": "Welcome to the JagCoaching API!"}

@app.get("/api/", response_description="API index route")
async def apiroutes():
    """Returns information about all available API endpoints."""
    return {
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "This index page showing all available endpoints and welcome message."
            },
            {
                "path": "/api/upload/",
                "method": "POST",
                "description": "Upload a video file"
            },
            {
                "path": "/api/process-audio/",
                "method": "POST",
                "description": "Extract and analyze speech from an uploaded video"
            },
            {
                "path": "/api/login/",
                "method": "POST",
                "description": "Login to the application"
            },
            {
                "path": "/api/logout/",
                "method": "POST",
                "description": "Logout the user from the application"
            },
            {
                "path": "/api/register/",
                "method": "POST",
                "description": "Register a new user account"
            },
            {
                "path": "/api/user/",
                "method": "GET",
                "description": "Check if the user is logged in"
            },
            {
                "path": "/api/profile/",
                "method": "GET",
                "description": "Get profile data for the logged in user"
            },
        ],
        "version": "1.0"
    }

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)