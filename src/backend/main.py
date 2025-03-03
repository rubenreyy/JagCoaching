from fastapi import FastAPI, UploadFile, File
import shutil
from pathlib import Path
from .config import settings
from .utils import extract_audio, transcribe_audio
from .models import UploadResponse, SpeechEvaluationRequest, SpeechEvaluationResponse
from transformers import pipeline
import whisper

app = FastAPI()

UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(exist_ok=True)

# Load models
whisper_model = whisper.load_model("base")
llm_pipeline = pipeline("text-generation", model=settings.LLM_MODEL)

@app.post("/upload/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handles video upload and saves it to the server."""
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/process-audio/")
def process_audio(file_name: str):
    """Extracts and processes audio from a video file."""
    video_path = UPLOAD_DIR / file_name
    audio_path = extract_audio(video_path)
    transcript = transcribe_audio(audio_path)
    return {"transcript": transcript, "audio_path": str(audio_path)}

@app.post("/evaluate-speech/", response_model=SpeechEvaluationResponse)
def evaluate_speech(request: SpeechEvaluationRequest):
    """Uses LLM to evaluate speech transcript."""
    prompt = f"""
    Evaluate the following speech based on clarity, coherence, engagement, and persuasiveness.
    Provide constructive feedback.

    Speech Transcript:
    {request.transcript}
    """
    response = llm_pipeline(prompt, max_length=300)
    feedback = response[0]['generated_text']
    return {"feedback": feedback}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)