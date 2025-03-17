from datetime import datetime
from pathlib import Path
import uuid
from typing import Optional, List, Dict, Any
from ..utils import extract_audio
from ..utils import transcribe_audio

class Video:
    """
    Data model representing a coaching video and its analysis results.
    """
    
    def __init__(
        self,
        file_path: Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.file_path = Path(file_path)
        self.title = title or self.file_path.stem
        self.description = description or ""
        self.tags = tags or []
        self.user_id = user_id
        self.upload_date = datetime.now()
        self.duration_seconds = None
        self.size_bytes = None
        
        # Analysis results
        self.audio_path = None
        self.transcription = None
        self.speech_analysis = None
        
        # Extract metadata if file exists
        if self.file_path.exists():
            self._extract_metadata()
    
    def _extract_metadata(self) -> None:
        """Extract basic metadata from the video file."""
        self.size_bytes = self.file_path.stat().st_size
        # Note: Duration would typically require a library like moviepy or ffprobe
        # self.duration_seconds = get_video_duration(self.file_path)
    
    def extract_audio(self) -> Path:
        """Extract audio from video file using utility function."""
        self.audio_path = extract_audio(self.file_path)
        return self.audio_path
    
    def transcribe(self) -> str:
        """Transcribe audio to text."""
        if not self.audio_path:
            self.extract_audio()
        self.transcription = transcribe_audio(self.audio_path)
        return self.transcription
    
    def analyze(self) -> Dict[str, Any]:
        """Perform full analysis on the video."""
        if not self.transcription:
            self.transcribe()
        
        # Placeholder for additional analysis
        # This could include sentiment analysis, keyword extraction, etc.
        self.speech_analysis = {
            "transcription": self.transcription,
            # Add other analysis results here
        }
        
        return self.speech_analysis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert video object to dictionary for serialization."""
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "user_id": self.user_id,
            "upload_date": self.upload_date.isoformat(),
            "duration_seconds": self.duration_seconds,
            "size_bytes": self.size_bytes,
            "transcription": self.transcription,
            "speech_analysis": self.speech_analysis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Video':
        """Create a Video object from dictionary data."""
        video = cls(file_path=data["file_path"])
        video.id = data.get("id", video.id)
        video.title = data.get("title", video.title)
        video.description = data.get("description", video.description)
        video.tags = data.get("tags", video.tags)
        video.user_id = data.get("user_id", video.user_id)
        if "upload_date" in data:
            video.upload_date = datetime.fromisoformat(data["upload_date"])
        video.duration_seconds = data.get("duration_seconds", video.duration_seconds)
        video.size_bytes = data.get("size_bytes", video.size_bytes)
        video.transcription = data.get("transcription", video.transcription)
        video.speech_analysis = data.get("speech_analysis", video.speech_analysis)
        return video