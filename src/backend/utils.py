from pathlib import Path
import logging
from pydub import AudioSegment
from scripts import speech_analysis
from scripts.SpeechAnalysisObject import SpeechAnalysisObject as SpeechAnalyzer

logger = logging.getLogger(__name__)

# TODO: extract audio and save into db for reference. assign it to new document and attach user id 

async def extract_audio(video_path: Path) -> Path:
    """Extracts audio from video and saves it as a WAV file."""
    try:
        logger.info(f"Starting audio extraction from {video_path}")
        
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if it doesn't exist
        output_dir = video_path.parent / "audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

        # Update audio_path to use the output directory
        audio_path = output_dir / video_path.with_suffix(".wav").name
        logger.info(f"Will save audio to: {audio_path}")
        
        audio = AudioSegment.from_file(video_path).export(str(audio_path), format="wav")
        logger.info(f"Audio extraction completed: {audio_path}")
        
        return audio_path
        
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}", exc_info=True)
        raise

async def analyze_audio(audio_path: Path) -> dict:
    """Analyzes audio using SpeechAnalysisObject and returns formatted feedback."""
    try:
        logger.info(f"Starting audio analysis for: {audio_path}")
        analysis = SpeechAnalyzer(str(audio_path))
        
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
                    else "Good clarity, but there's room for improvement." if analysis.clarity > 70
                    else "Consider speaking more clearly and enunciating your words."
                )
            }
        }
        
        logger.info("Audio analysis completed successfully")
        return feedback_data
        
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}", exc_info=True)
        raise
def transcribe_audio(audio_path: Path) -> str:
    """Transcribes audio to text using Whisper."""
    result = speech_analysis.transcribe_speech(str(audio_path)) # replaced with project script
    return result["text"]
