from typing import List, Dict, Any
from pathlib import Path
import shutil
import os
import uuid
import logging
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from models.user_models import UserResponse as User
from database.cloud_db_controller import CloudDBController
from dependencies.auth import get_current_active_user
from models import FileName
from models.schemas import UploadResponse
from scripts.powerpoint_analysis.pptx_analysis import analyze_presentation

router = APIRouter(
    prefix="/api/presentations",
    tags=["presentations"],
    responses={404: {"description": "Not found"}},
)

# Configure presentation storage path
UPLOAD_DIR = Path("uploads/presentations")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_CONNECTION = CloudDBController()

logger = logging.getLogger(__name__)

@router.post("/upload/", response_model=UploadResponse, response_description="Upload PowerPoint presentation")
async def upload_presentation(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Handles PowerPoint presentation upload and saves it to the server."""
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

        # Create a presentation document
        presentation_doc = {
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
        presentation_result = DB_CONNECTION.add_document("JagCoaching", "presentations_files", presentation_doc)
        logger.info(f"Presentation saved to database with ID: {presentation_result.inserted_id}")

        return {"filename": unique_filename, "status": "uploaded"}

    except Exception as e:
        logger.error(f"Error during upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

@router.post("/analyze/", response_description="Analyze PowerPoint presentation")
async def analyze_ppt(
    file_name: FileName,
    current_user: User = Depends(get_current_active_user)
):
    """Analyzes a PowerPoint presentation"""
    logger.info(f"Starting presentation analysis for file: {file_name.file_name}")
    try:
        # First try to find the presentation with the UUID filename
        presentation_path = UPLOAD_DIR / file_name.file_name
        logger.info(f"Looking for presentation at: {presentation_path}")
        
        if not presentation_path.exists():
            # If not found, try to find the most recent presentation uploaded by this user
            logger.info(f"Presentation not found at {presentation_path}, looking for recent uploads")
            DB_CONNECTION.connect()
            user_id = str(current_user["_id"])
            
            # Get all presentations for this user
            presentations = list(DB_CONNECTION.find_documents(
                "JagCoaching", 
                "presentations_files", 
                {"user_id": user_id}
            ))
            
            # Sort manually by upload_date (newest first)
            if presentations:
                presentations.sort(key=lambda x: x.get("upload_date", datetime.min), reverse=True)
                presentation = presentations[0]
                presentation_id = str(presentation["_id"])
                stored_path = presentation.get("file_path")
                if stored_path:
                    presentation_path = Path(stored_path)
                    if not presentation_path.exists() and not presentation_path.is_absolute():
                        # Try with the uploads prefix if it's a relative path
                        presentation_path = UPLOAD_DIR / Path(stored_path).name
                logger.info(f"Found recent presentation: {presentation_path}")
            
            if not presentation_path.exists():
                logger.error(f"Presentation file not found: {presentation_path}")
                raise HTTPException(status_code=404, detail="Presentation file not found")
        
        # Analyze presentation
        logger.info("Starting presentation analysis...")
        analysis_result = analyze_presentation(str(presentation_path))
        logger.info("Presentation analysis completed")
        
        # Add feedback_type to identify this as presentation feedback
        analysis_result["feedback_type"] = "presentation"
        
        # Update database with analysis results
        logger.info("Updating database with analysis results...")
        DB_CONNECTION.connect()
        
        # Create a presentation analysis record
        presentation_analysis = {
            "user_id": str(current_user["_id"]),
            "file_path": str(presentation_path),
            "title": os.path.basename(presentation_path),
            "feedback_data": analysis_result,
            "created_at": datetime.now(),
            "date": datetime.now().isoformat()
        }
        
        # Insert the presentation analysis record
        analysis_result_db = DB_CONNECTION.add_document("JagCoaching", "presentations_analysis", presentation_analysis)
        analysis_id = str(analysis_result_db.inserted_id)
        
        # Add analysis_id to the response
        analysis_result["analysis_id"] = analysis_id
        
        logger.info("Database updated successfully")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing presentation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close()

@router.get("/analysis/", response_description="Get all PowerPoint presentation analyses for the current user")
async def get_presentation_analyses(
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all PowerPoint presentation analyses for the current user."""
    logger.info(f"Fetching presentation analyses for user: {current_user}")
    
    try:
        DB_CONNECTION.connect()
        user_id = str(current_user["_id"])
        
        # Get all presentation analyses for this user
        analyses = list(DB_CONNECTION.find_documents(
            "JagCoaching", 
            "presentations_analysis", 
            {"user_id": user_id}
        ))
        
        # Convert ObjectId to string for JSON serialization
        for analysis in analyses:
            analysis["_id"] = str(analysis["_id"])
            if "created_at" in analysis and isinstance(analysis["created_at"], datetime):
                analysis["created_at"] = analysis["created_at"].isoformat()
        
        logger.info(f"Found {len(analyses)} presentation analyses")
        return analyses
        
    except Exception as e:
        logger.error(f"Error fetching presentation analyses: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch analyses: {str(e)}")
    finally:
        if DB_CONNECTION.client:
            DB_CONNECTION.client.close() 