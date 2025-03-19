from pydub import AudioSegment
from scripts import speech_analysis
from pathlib import Path


# removed whisper import

async def extract_audio(video_path: Path) -> Path:
    """Extracts audio from video and saves it as a WAV file."""
    # Create output directory if it doesn't exist
    output_dir = video_path.parent / "audio"
    output_dir.mkdir(exist_ok=True)

    # Update audio_path to use the output directory
    audio_path = output_dir / video_path.with_suffix(".wav").name
    audio = AudioSegment.from_file(video_path).export(audio_path, format="wav")
    print(audio)
    return audio.name

def transcribe_audio(audio_path: Path) -> str:
    """Transcribes audio to text using Whisper."""
    result = speech_analysis.transcribe_speech(str(audio_path)) # replaced with project script
    return result["text"]