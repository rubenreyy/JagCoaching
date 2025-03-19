# Include the project root directory in the Python path if testing this file only
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(
        os.path.abspath("JagCoaching/scripts"))))

# Built-in imports
from contextlib import asynccontextmanager
import shutil
from pathlib import Path

# third-party imports
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
# from routers import users_router, auth_router , videos_router
from dependencies.auth import get_current_user
from routers import videos_router , auth_router


# Local imports
from config import settings
from utils import extract_audio
from modelsold import FileName, UploadResponse
from models.user import test_user , User
from scripts import speech_analysis, SpeechAnalysisObject


UPLOAD_DIR = None



# Startup and shutdown event handlers for fastapi
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the upload directory on startup."""
    global UPLOAD_DIR
    UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
    UPLOAD_DIR.mkdir(exist_ok=True)
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

# TODO: Include the routers in the main FastAPI application when database is working
# app.include_router(users_router)
app.include_router(auth_router)
# app.include_router(videos_router)


# Added CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Index route
@app.get("/")
async def index():
    return {"message": "Welcome to the JagCoaching API!"}

# API route
@app.get("/api/")
async def index():
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


# Get profile data for the logged in user
@app.get("/api/profile/")
def get_profile():
    """Returns the profile data for the currently logged in user."""

    return {
        "status": "success",
        "user": {
            "username": test_user["username"],
            "email": test_user["email"],
            "name": "Test User",
            "created_at": "2023-01-01T00:00:00Z",
            "last_login": "2023-03-15T10:30:00Z",
            "preferences": test_user.get("preferences", {})
        }
    }

# Changed the endpoint to /api/upload/ to match the frontend
@app.post("/api/upload/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handles video upload and saves it to the server."""
    # Create the upload directory if it doesn't exist
    global UPLOAD_DIR
    
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"}
    

# Changed the endpoint to /api/process-audio/ to match the frontend
@app.post("/api/process-audio/")
async def process_audio(file_name: FileName):
    """Extracts and analyzes speech from uploaded video"""
    global UPLOAD_DIR
    print(file_name)

    video_path = UPLOAD_DIR / file_name.file_name
    audio_path = await extract_audio(video_path)
    
    # Run AI analysis
    analysis = SpeechAnalysisObject.SpeechAnalysisObject(audio_path)

    print(analysis)    

    # Generate feedback
    # feedback = analysis.generate_feedback()
    
   
    # Format the feedback as a JSON-serializable dictionary
    feedback_data = {
        "transcript": analysis.transcript,
        "sentiment": analysis.sentiment,
        "filler_words": analysis.filler_words,
        "emotion": analysis.emotion,
        "keywords": analysis.keywords,
        "pauses": analysis.pauses,
        "wpm": analysis.wpm,
        "clarity": analysis.clarity,
    }
    
    # JSON response
    return {"feedback": feedback_data}


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000,reload=True)
