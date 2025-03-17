# Revised on March 15 to trigger AI analysis when the video is uploaded

# FIXME: Added overview of all available endpoints, changed default LLM for now with ungated repo, added os and sys imports to append paths for scripts

# Include the project root directory in the Python path if testing this file only
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("JagCoaching/scripts"))))
    # -- Uncomment to print the Python paths --
    # for path in sys.path: 
    #     print(path)
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File , Depends , APIRouter , Request
from fastapi.middleware.cors import CORSMiddleware
import shutil
# from routers import users_router, auth_router , videos_router
from pathlib import Path
from config import settings
from utils import extract_audio
from modelsold import FileName, UploadResponse, SpeechEvaluationRequest, SpeechEvaluationResponse, User
from scripts import speech_analysis , SpeechAnalysisObject
import uuid

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
# app.include_router(auth_router)
# app.include_router(videos_router)

# Test user data for account page
test_user = {
    "username": "jagcoaching",
    "email": "jagcoaching@example.com",
    "password": "securepassword"
}


# Added CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

@app.get("/")
async def index():
    return {"message": "Welcome to the JagCoaching API!"}


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
        ],
        "version": "1.0"
    }


# Login endpoint
@app.post("/api/login/")
def login(form: User):
    print(form)
    
    return {"status": "success", "message": "Login successful!"}

# Signup endpoint
@app.post("/api/register/")
# def register(username: str, email: str, password: str):
def register(form: User):
    username = form.username
    email = form.email
    password = form.password
    print(username, email, password)
    return {"status": "success", "message": "Registration successful!", "user": {"username": username, "email": email}}


# Check if the user is logged in
@app.get("/api/user/")
def get_user_info(username: str = Depends(login)):
    if not username:
        return {"status": "error", "message": "User not found!"}
    else:
        return {"status": "success", "message": "User found!"}

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
            "last_login": "2023-03-15T10:30:00Z"
        }
    }

# Changed the endpoint to /api/upload/ to match the frontend
@app.post("/api/upload/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handles video upload and saves it to the server."""
    # Create the upload directory if it doesn't exist
    global UPLOAD_DIR
    # Create a unique filename to prevent overwriting
    # unique_filename = f"{uuid.uuid4()}_{file.filename}"
    # file_path = UPLOAD_DIR / unique_filename
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
    analysis = await SpeechAnalysisObject.SpeechAnalysisObject(audio_path)
    
    # Generate feedback
    feedback = analysis.generate_feedback()
    
    return {
        "transcript": analysis.transcript,
        "sentiment": analysis.sentiment,
        "filler_words": analysis.filler_words,
        "emotion": analysis.emotion,
        "keywords": analysis.keywords,
        "pauses": analysis.pauses,
        "wpm": analysis.wpm,
        "clarity": analysis.clarity,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
