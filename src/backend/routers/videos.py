from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import os
import uuid
import sys

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from models.user_models import UserResponse as User
from dependencies.auth import get_current_user
from models import FileName, VideoCreate
from models.video_models import Video
from models.schemas import UploadResponse
from utils import extract_audio
from scripts import SpeechAnalysisObject

router = APIRouter(
    prefix="/api/videos",  # Changed from "/videos" to "/api/upload"
    tags=["videos"],
    responses={404: {"description": "Not found"}},
)

# Configure video storage path
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# FIXME: Add authentication back to make it work for uploads
# async def upload_video(
#     file: UploadFile = File(...),
#     current_user: User = Depends(get_current_user)
# ):
    # """Handles video upload and saves it to the server."""
    # # User authentication is now handled by the dependency
    # if not current_user:
    #     raise HTTPException(status_code=401, detail="User not logged in")

# Upload video file route
@router.post("/upload/", response_model=UploadResponse, response_description="File upload to server & extracts audio")
async def upload_video(
    file: UploadFile = File(...)
):
    """Handles video upload and saves it to the server."""

    # Create the upload directory if it doesn't exist
    print("uploading video")

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename


    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer) 

    # Create a new video object and insert into the database
    video = VideoCreate(
        file_path=file_path,
        title=file.filename,
        description=None,
        tags=[],
        # user_id=current_user.id  # Use the current user's ID FIXME: need to add auth back for this 
    )
    
    return {"filename": unique_filename, "status": "uploaded"}



# Changed the endpoint to /api/process-audio/ to match the frontend
@router.post("/process-audio/", response_description="Analyze speech from uploaded video through model")
async def process_audio(file_name: FileName):
    """Extracts and analyzes speech from uploaded video"""
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

@router.get("/", response_model=List[Dict[str, Any]])
async def list_videos(user_id: Optional[str] = None , response_description="List all videos, optionally filtered by user_id"):
    """List all videos, optionally filtered by user_id."""
    # TODO: Implement video listing based on user_id or JWT
    return []


@router.get("/{video_id}", response_model=Dict[str, Any])
async def get_video(video_id: str):
    """Get a specific video by ID."""
    # TODO: Implement video retrieval based on video_id
    raise HTTPException(status_code=404, detail=f"Video {video_id} not found")


@router.post("/{video_id}/analyze")
async def analyze_video(video_id: str, background_tasks: BackgroundTasks):
    """Start analyzing a video in the background."""
    # This is a placeholder - you would typically find the video in your storage/database
    # Then start the analysis process
    # For demonstration, we'll just acknowledge the request
    background_tasks.add_task(run_video_analysis, video_id)
    return {"status": "Analysis started", "video_id": video_id}


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Delete a video by ID."""
    # This is a placeholder - you would find and delete the video
    # TODO: Implement video deletion based on video_id
    return {"status": "deleted", "video_id": video_id}


# Background tasks (Currently not in use yet)
async def process_video(video_id: str, file_path: Path):
    """Process a newly uploaded video (extract metadata, etc.)."""
    # This would be implemented based on your Video class functionality
    print(video_id)

    video_path = UPLOAD_DIR / file_path.name
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
    pass


def run_video_analysis(video_id: str):
    """Run the full analysis pipeline on a video."""
    # This would load the video and call its analyze() method
    pass
