from datetime import datetime
from pathlib import Path
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

# -- INFO: Models for video data and processing -- #

# PyObjectId class for handling MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

# Base Video model
class VideoBase(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    user_id: Optional[str] = None

# Model for creating a new video
class VideoCreate(VideoBase):
    file_path: str

# Model for updating a video
class VideoUpdate(VideoBase):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    

    
# Model for a video stored in the database
class VideoInDB(VideoBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    file_path: str
    upload_date: datetime = Field(default_factory=datetime.now)
    duration_seconds: Optional[float] = None
    size_bytes: Optional[int] = None
    audio_path: Optional[str] = None
    transcription: Optional[str] = None
    speech_analysis: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "60d5ec2af682fbedea4216c8",
                "title": "Coaching Session 1",
                "description": "Initial coaching session",
                "tags": ["interview", "feedback"],
                "user_id": "60d5ec2af682fbedea4216c7",
                "file_path": "/videos/session1.mp4",
                "upload_date": "2023-04-01T10:30:00",
                "duration_seconds": 300,
                "size_bytes": 15000000,
                "audio_path": "/audio/session1.wav",
                "transcription": "Hello, welcome to the coaching session...",
                "speech_analysis": {"key_points": ["confidence", "clarity"]}
            }
        }

# Model for returning video data
class Video(VideoBase):
    id: str = Field(alias="_id")
    file_path: str
    upload_date: datetime
    duration_seconds: Optional[float] = None
    size_bytes: Optional[int] = None
    audio_path: Optional[str] = None
    transcription: Optional[str] = None
    speech_analysis: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Helper functions for video processing
def extract_video_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract basic metadata from the video file."""
    metadata = {}
    if Path(file_path).exists():
        metadata["size_bytes"] = Path(file_path).stat().st_size
        # Note: Duration would typically require a library like moviepy or ffprobe
        # metadata["duration_seconds"] = get_video_duration(file_path)
    return metadata
