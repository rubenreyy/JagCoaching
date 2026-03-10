from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import os
import uuid
import sys
from bson import ObjectId
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from models.user_models import UserResponse as User
from database.cloud_db_controller import CloudDBController
from dependencies.auth import get_current_user , get_current_active_user
from models import FileName, VideoCreate
from models.video_models import Video
from models.schemas import UploadResponse
from utils import extract_audio, analyze_audio
from scripts.SpeechAnalysisObject import SpeechAnalysisObject as SpeechAnalyzer

router = APIRouter(
    prefix="/api/videos",  # Changed from "/videos" to "/api/upload"
    tags=["videos"],
    responses={404: {"description": "Not found"}},
)

# Configure video storage path
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_CONNECTION = CloudDBController()

logger = logging.getLogger(__name__)

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
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Handles video upload and saves it to the server."""
    logger.info(f"Upload request received from user: {current_user}")
    logger.info(f"File details - Filename: {file.filename}, Content-Type: {file.content_type}")

    if current_user is None:
        logger.error("User not authenticated")
        raise HTTPException(status_code=401, detail="User not logged in")
    
    try:
        # Create the upload directory if it doesn't exist
        logger.info("Creating upload directory")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        logger.info(f"Generated unique filename: {unique_filename}")
        
        file_path = UPLOAD_DIR / unique_filename
        logger.info(f"Saving file to: {file_path}")

        # Save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("File saved successfully")

        # Create a video document
        video_doc = {
            "title": file.filename,
            "description": "",
            "file_path": str(file_path),
            "user_id": str(current_user["_id"]),
            "upload_date": datetime.now(),
            "size_bytes": os.path.getsize(file_path),
            "tags": []
        }

        # Save to database
        logger.info("Connecting to database")
        DB_CONNECTION.connect()
        video_result = DB_CONNECTION.add_document("JagCoaching", "videos", video_doc)
        logger.info(f"Video saved to database with ID: {video_result.inserted_id}")

        return {"filename": unique_filename, "status": "uploaded"}

    except Exception as e:
        logger.error(f"Error during upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()



# Changed the endpoint to /api/process-audio/ to match the frontend
@router.post("/process-audio/", response_description="Analyze speech from uploaded video")
async def process_audio(
    file_name: FileName,
    current_user: User = Depends(get_current_active_user)
):
    """Extracts and analyzes speech from uploaded video"""
    logger.info(f"Starting audio processing for file: {file_name.file_name}")
    try:
        # First try to find the video with the UUID filename
        video_path = UPLOAD_DIR / file_name.file_name
        logger.info(f"Looking for video at: {video_path}")
        
        if not video_path.exists():
            # If not found, try to find the most recent video uploaded by this user
            logger.info(f"Video not found at {video_path}, looking for recent uploads")
            DB_CONNECTION.connect()
            user_id = str(current_user["_id"])
            
            # Get all videos for this user
            videos = list(DB_CONNECTION.find_documents(
                "JagCoaching", 
                "videos", 
                {"user_id": user_id}
            ))
            
            # Sort manually by upload_date (newest first)
            if videos:
                videos.sort(key=lambda x: x.get("upload_date", datetime.min), reverse=True)
                video = videos[0]
                video_id = str(video["_id"])
                stored_path = video.get("file_path")
                if stored_path:
                    video_path = Path(stored_path)
                    if not video_path.exists() and not video_path.is_absolute():
                        # Try with the uploads prefix if it's a relative path
                        video_path = UPLOAD_DIR / Path(stored_path).name
                logger.info(f"Found recent video: {video_path}")
            
            if not video_path.exists():
                logger.error(f"Video file not found: {video_path}")
                raise HTTPException(status_code=404, detail="Video file not found")
            
        # Extract audio
        logger.info("Starting audio extraction...")
        audio_path = await extract_audio(video_path)
        logger.info(f"Audio extracted successfully to: {audio_path}")

        # Analyze audio
        logger.info("Starting audio analysis...")
        analysis = SpeechAnalyzer(str(audio_path))
        
        # Format the feedback to match mockFeedbackData structure
        feedback_data = {
            "transcript": analysis.transcript,
            "sentiment": {
                "label": analysis.sentiment["label"],
                "score": analysis.sentiment["score"],
                "suggestion": analysis.sentiment["suggestion"]
            },
            "filler_words": {
                "counts": analysis.filler_words["counts"],
                "total": analysis.filler_words["total"],
                "suggestion": analysis.filler_words["suggestion"]
            },
            "speech_rate": {
                "wpm": analysis.wpm["wpm"],
                "assessment": analysis.wpm["assessment"],
                "suggestion": analysis.wpm["suggestion"]
            },
            "keywords": {
                "topics": analysis.keywords,
                "context": "These key topics represent the main themes discussed in your presentation."
            },
            "clarity": {
                "score": analysis.clarity,
                "suggestion": (
                    "Excellent clarity! Your speech is very well articulated." if analysis.clarity > 90
                    else "Good clarity. Minor improvements in pronunciation could help." if analysis.clarity > 75
                    else "Consider speaking more clearly and deliberately."
                )
            }
        }
        logger.info("Audio analysis completed")

        # Update database with analysis results and associate with user
        logger.info("Updating database with analysis results...")
        DB_CONNECTION.connect()
        
        # Create a presentation record with more metadata
        presentation_data = {
            "user_id": str(current_user["_id"]),
            "video_id": video_id,
            "title": os.path.basename(video_path),
            "feedback_data": feedback_data,
            "created_at": datetime.now(),
            "date": datetime.now().isoformat(),  # Add a formatted date string for easier frontend use
            "score": calculate_overall_score(feedback_data),  # Calculate an overall score
            "summary": generate_summary(feedback_data)  # Generate a brief summary
        }
        
        # Insert the presentation record
        presentation_result = DB_CONNECTION.add_document("JagCoaching", "presentations", presentation_data)
        presentation_id = str(presentation_result.inserted_id)
        
        # Also update the video document
        DB_CONNECTION.update_document(
            "JagCoaching", 
            "videos", 
            {"_id": ObjectId(video_id)}, 
            {
                "analysis_results": feedback_data,
                "presentation_id": presentation_id  # Link to the presentation
            }
        )
        
        # Add presentation_id to the response
        feedback_data["presentation_id"] = presentation_id
        
        logger.info("Database updated successfully")
        return feedback_data

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

# Helper functions for presentation data
def calculate_overall_score(feedback_data):
    """Calculate an overall score from feedback data"""
    try:
        # Example scoring logic - customize based on your feedback structure
        clarity_score = feedback_data.get("clarity", {}).get("score", 0)
        sentiment_score = 0
        sentiment = feedback_data.get("sentiment", {})
        if sentiment:
            if sentiment.get("label") == "Positive":
                sentiment_score = 90
            elif sentiment.get("label") == "Neutral":
                sentiment_score = 70
            else:
                sentiment_score = 50
        
        # Calculate average score
        return round((clarity_score + sentiment_score) / 2)
    except Exception as e:
        logger.error(f"Error calculating score: {str(e)}")
        return 75  # Default score

def generate_summary(feedback_data):
    """Generate a brief summary from feedback data"""
    try:
        summary_parts = []
        
        # Add sentiment
        sentiment = feedback_data.get("sentiment", {}).get("label", "")
        if sentiment:
            summary_parts.append(f"{sentiment} tone")
        
        # Add speech rate assessment
        speech_rate = feedback_data.get("speech_rate", {}).get("assessment", "")
        if speech_rate:
            summary_parts.append(f"{speech_rate} pace")
        
        # Add filler word assessment
        filler_count = feedback_data.get("filler_words", {}).get("total", 0)
        if filler_count > 5:
            summary_parts.append("many filler words")
        elif filler_count > 0:
            summary_parts.append("some filler words")
        
        # Create summary string
        if summary_parts:
            return ", ".join(summary_parts)
        return "Analysis complete"
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Analysis complete"

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
    analysis = SpeechAnalyzer(audio_path)

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

@router.get("/presentations/", response_model=List[Dict[str, Any]])
async def get_user_presentations(
    limit: int = Query(10, ge=0),
    skip: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Get all presentations for the current user"""
    try:
        DB_CONNECTION.connect()
        user_id = str(current_user["_id"])
        
        # Determine sort option
        sort_option = None
        if sort_by == "date-desc":
            sort_option = ("created_at", -1)
        elif sort_by == "date-asc":
            sort_option = ("created_at", 1)
        elif sort_by == "score-desc":
            sort_option = ("score", -1)
        elif sort_by == "score-asc":
            sort_option = ("score", 1)
        
        # Retrieve presentations for this user
        presentations = DB_CONNECTION.get_user_presentations(
            "JagCoaching", 
            user_id, 
            limit=limit,
            skip=skip,
            sort_by=sort_option
        )
        
        # Convert ObjectId to string for JSON serialization
        for presentation in presentations:
            if "_id" in presentation:
                presentation["_id"] = str(presentation["_id"])
        
        return presentations
    except Exception as e:
        logger.error(f"Error retrieving presentations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presentations: {str(e)}")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

@router.get("/presentations/{presentation_id}", response_model=Dict[str, Any])
async def get_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific presentation by ID"""
    try:
        DB_CONNECTION.connect()
        user_id = str(current_user["_id"])
        
        # Retrieve the presentation
        presentation = DB_CONNECTION.get_presentation_by_id("JagCoaching", presentation_id)
        
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if the presentation belongs to the current user
        if presentation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this presentation")
        
        # Convert ObjectId to string for JSON serialization
        if "_id" in presentation:
            presentation["_id"] = str(presentation["_id"])
        
        return presentation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving presentation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presentation: {str(e)}")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()
