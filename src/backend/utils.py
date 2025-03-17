from pydub import AudioSegment
from scripts import speech_analysis
from pathlib import Path

# removed whisper import

def extract_audio(video_path: Path) -> Path:
    """Extracts audio from video and saves it as a WAV file."""
    audio_path = video_path.with_suffix(".wav")
    AudioSegment.from_file(video_path).export(audio_path, format="wav")
    return audio_path

def transcribe_audio(audio_path: Path) -> str:
    """Transcribes audio to text using Whisper."""
    result = speech_analysis.transcribe_speech(str(audio_path)) # replaced with project script
    return result["text"]