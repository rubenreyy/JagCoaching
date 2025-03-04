from pydub import AudioSegment
import whisper
from pathlib import Path

whisper_model = whisper.load_model("base")

def extract_audio(video_path: Path) -> Path:
    """Extracts audio from video and saves it as a WAV file."""
    audio_path = video_path.with_suffix(".wav")
    AudioSegment.from_file(video_path).export(audio_path, format="wav")
    return audio_path

def transcribe_audio(audio_path: Path) -> str:
    """Transcribes audio to text using Whisper."""
    result = whisper_model.transcribe(str(audio_path))
    return result["text"]