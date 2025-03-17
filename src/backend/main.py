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

from fastapi import FastAPI, UploadFile, File , Depends
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from config import settings
from utils import extract_audio
from models import UploadResponse, SpeechEvaluationRequest, SpeechEvaluationResponse
from scripts import speech_analysis , SpeechAnalysisObject

app = FastAPI()
UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(exist_ok=True)


# Added CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
                "description": "This index page showing all available endpoints"
            },
            {
                "path": "/upload/",
                "method": "POST",
                "description": "Upload a video file"
            },
            {
                "path": "/process-audio/",
                "method": "POST",
                "description": "Extract and analyze speech from an uploaded video"
            },
            {
                "path": "/evaluate-speech/",
                "method": "POST",
                "description": "Evaluate speech transcript using LLM"
            }
        ],
        "version": "1.0"
    }


# Login endpoint
@app.post("/api/login/")
def login(username: str, password: str, ):
    print(username,password)
    return {"status": "success", "message": "Login successful!"}

# Signup endpoint
@app.post("/api/register/")
def register(username: str, email: str, password: str):
    print(username, email, password)
    return {"status": "success", "message": "Registration successful!"}


# Check if the user is logged in
@app.get("/api/user/")
def get_user(username: str = Depends()):
    if not username:
        return {"status": "error", "message": "User not found!"}
    
    return {"status": "success", "message": "User found!"}

# Changed the endpoint to /api/upload/ to match the frontend
@app.post("/api/upload/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handles video upload and saves it to the server."""
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"}

# Changed the endpoint to /api/process-audio/ to match the frontend
@app.post("/api/process-audio/")
def process_audio(file_name: str):
    """Extracts and analyzes speech from uploaded video"""
    video_path = UPLOAD_DIR / file_name
    audio_path = extract_audio(video_path)

    # Run AI analysis
    analysis = SpeechAnalysisObject(audio_path)
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


@app.post("/api/process-audio/")
def process_audio(file_name: str):
    """Extracts and analyzes speech from uploaded video"""
    video_path = UPLOAD_DIR / file_name
    audio_path = extract_audio(video_path)

    # Run AI analysis
    analysis = SpeechAnalysisObject(audio_path)
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

@app.post("/evaluate-speech/", response_model=SpeechEvaluationResponse)
def evaluate_speech(request: SpeechEvaluationRequest):
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
