import sys
import os

# Include the project root directory in the Python path if testing this file only
if sys.path.count(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) == 0:
    sys.path.append(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))

# Third-party and local imports
from config import settings
from routers import auth_router, videos_router, users_router
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
logger = logging.getLogger(__name__)

# Load .env
dotenv.load_dotenv("./env.development")

UPLOAD_DIR = settings.UPLOAD_FOLDER

# Startup and shutdown event handlers for fastapi
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create necessary directories on startup."""
    try:
        upload_path = Path(settings.UPLOAD_FOLDER)
        video_path = upload_path / "videos"
        audio_path = video_path / "audio"

        for directory in [upload_path, video_path, audio_path]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        yield
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error in lifespan: {str(e)}")
        raise

# Initialize app
app = FastAPI(lifespan=lifespan)

# Include routers with /api prefix
app.include_router(users_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(videos_router, prefix="/api")

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Optional manual headers
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Root Index Route
@app.get("/")
async def index():
    return {"message": "Welcome to the JagCoaching API!"}

# API route info
@app.get("/api/", response_description="API index route")
async def apiroutes():
    return {
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Welcome message"},
            {"path": "/api/upload/", "method": "POST", "description": "Upload a video file"},
            {"path": "/api/process-audio/", "method": "POST", "description": "Analyze uploaded video audio"},
            {"path": "/api/login/", "method": "POST", "description": "User login"},
            {"path": "/api/logout/", "method": "POST", "description": "User logout"},
            {"path": "/api/register/", "method": "POST", "description": "Register a user"},
            {"path": "/api/user/", "method": "GET", "description": "Get current user"},
            {"path": "/api/profile/", "method": "GET", "description": "User profile info"}
        ],
        "version": "1.0"
    }

# Run as script
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
