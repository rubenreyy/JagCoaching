from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import os
import uuid
from models.video import Video
from dependencies import get_current_user
from scripts import SpeechAnalysisObject
from scripts import speech_analysis

router = APIRouter(
    prefix="/api/upload",  # Changed from "/videos" to "/api/upload"
    tags=["videos"],
    responses={404: {"description": "Not found"}},
)

# Configure video storage path
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=Dict[str, Any])
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    """Upload a new video file and optionally start processing it."""
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse tags if provided
    tags_list = tags.split(",") if tags else []
    
    # Create video object
    video = Video(
        file_path=file_path,
        title=title,
        description=description,
        tags=tags_list,
        user_id=user_id
    )
    
    # Start background processing
    background_tasks.add_task(process_video, video.id, file_path)
    
    return video.to_dict()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_videos(user_id: Optional[str] = None):
    """List all videos, optionally filtered by user_id."""
    # This is a placeholder - you would typically query from a database
    # For demonstration, we'll return an empty list
    return []


@router.get("/{video_id}", response_model=Dict[str, Any])
async def get_video(video_id: str):
    """Get a specific video by ID."""
    # This is a placeholder - you would typically query from a database
    # For demonstration purposes, we'll raise a not found error
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
    # For demonstration, we'll just acknowledge the request
    return {"status": "deleted", "video_id": video_id}


# Background tasks
def process_video(video_id: str, file_path: Path):
    """Process a newly uploaded video (extract metadata, etc.)."""
    # This would be implemented based on your Video class functionality
    pass


def run_video_analysis(video_id: str):
    """Run the full analysis pipeline on a video."""
    # This would load the video and call its analyze() method
    pass