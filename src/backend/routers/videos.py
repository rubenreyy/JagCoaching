import os
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from models.user_models import UserResponse as User
from database.cloud_db_controller import CloudDBController
from dependencies.auth import get_current_active_user
from models import FileName, VideoCreate
from models.video_models import Video
from models.schemas import UploadResponse
from utils import extract_audio
from scripts.SpeechAnalysisObject import SpeechAnalysisObject as SpeechAnalyzer

# Router setup
router = APIRouter(
    prefix="/videos",
    tags=["videos"],
    responses={404: {"description": "Not found"}},
)

# Logging
logger = logging.getLogger(__name__)

# File paths
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# DB
DB_CONNECTION = CloudDBController()

# ----------------------------
# Upload Video
# ----------------------------

@router.post("/upload/", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload video and extract audio"""
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not logged in")

    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Saved uploaded file to: {file_path}")

        # Add to DB
        DB_CONNECTION.connect()
        result = DB_CONNECTION.add_document("JagCoaching", "videos", {
            "title": file.filename,
            "description": "",
            "file_path": str(file_path),
            "user_id": str(current_user["_id"]),
            "upload_date": datetime.now(),
            "size_bytes": os.path.getsize(file_path),
            "tags": []
        })

        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to save video")

        return UploadResponse(filename=unique_filename, status="uploaded")

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

# ----------------------------
# Process Audio
# ----------------------------

@router.post("/process-audio/", response_description="Analyze speech from uploaded video")
async def process_audio(
    file_name: FileName,
    current_user: User = Depends(get_current_active_user)
):
    video_path = UPLOAD_DIR / file_name.file_name

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    try:
        audio_path = await extract_audio(video_path)
        analysis = SpeechAnalyzer(str(audio_path))

        feedback_data = {
            "transcript": analysis.transcript,
            "sentiment": analysis.sentiment,
            "filler_words": analysis.filler_words,
            "speech_rate": analysis.wpm,
            "keywords": {
                "topics": analysis.keywords,
                "context": "These key topics represent the main themes discussed in your presentation."
            },
            "clarity": {
                "score": analysis.clarity,
                "suggestion": (
                    "Excellent clarity!" if analysis.clarity > 90 else
                    "Good clarity." if analysis.clarity > 75 else
                    "Consider speaking more clearly."
                )
            }
        }

        # Save results to DB
        DB_CONNECTION.connect()
        DB_CONNECTION.update_document(
            "JagCoaching",
            "videos",
            {"file_path": str(video_path), "user_id": str(current_user["_id"])},
            {
                "audio_path": str(audio_path),
                "analysis_results": feedback_data,
                "updated_at": datetime.now()
            }
        )

        return feedback_data

    except Exception as e:
        logger.error(f"Audio processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Processing failed")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

# ----------------------------
# List Videos (placeholder)
# ----------------------------

@router.get("/", response_model=List[Dict[str, Any]])
async def list_videos(user_id: Optional[str] = None):
    """List uploaded videos (optional filter by user)"""
    return []  # TODO

# ----------------------------
# Get Specific Video (placeholder)
# ----------------------------

@router.get("/{video_id}", response_model=Dict[str, Any])
async def get_video(video_id: str):
    raise HTTPException(status_code=404, detail="Not implemented")

# ----------------------------
# Trigger Async Analysis (placeholder)
# ----------------------------

@router.post("/{video_id}/analyze")
async def analyze_video(video_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_video_analysis, video_id)
    return {"status": "Analysis started", "video_id": video_id}

# ----------------------------
# Delete Video (placeholder)
# ----------------------------

@router.delete("/{video_id}")
async def delete_video(video_id: str):
    return {"status": "deleted", "video_id": video_id}

# ----------------------------
# Background Analysis Task (placeholder)
# ----------------------------

async def process_video(video_id: str, file_path: Path):
    """(future) AI pipeline processing"""
    analysis = SpeechAnalyzer(str(file_path))
    return {
        "feedback": {
            "transcript": analysis.transcript,
            "sentiment": analysis.sentiment,
            "filler_words": analysis.filler_words,
            "emotion": analysis.emotion,
            "keywords": analysis.keywords,
            "pauses": analysis.pauses,
            "wpm": analysis.wpm,
            "clarity": analysis.clarity,
        }
    }

def run_video_analysis(video_id: str):
    """(future) Non-async placeholder"""
    pass
