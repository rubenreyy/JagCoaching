# Revised on March 15 to trigger AI analysis when the video is uploaded

# FIXME: Added overview of all available endpoints, changed default LLM for now with ungated repo, added os and sys imports to append paths for scripts

# Include the project root directory in the Python path if testing this file only
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("JagCoaching/scripts"))))
    # -- Uncomment to print the Python paths --
    # for path in sys.path: 
    #     print(path)

from fastapi import FastAPI, UploadFile, File
import shutil
from pathlib import Path
from config import settings
from utils import extract_audio
from models import UploadResponse, SpeechEvaluationRequest, SpeechEvaluationResponse
from scripts import speech_analysis , SpeechAnalysisObject
from transformers import pipeline
import whisper

app = FastAPI()
UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(exist_ok=True)

# Load models
whisper_model = whisper.load_model("base")
llm_pipeline = pipeline("text-generation", model=settings.LLM_MODEL)


@app.get("/api/")
async def index():
    """Returns information about all available API endpoints."""
    return {
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "This index page showing all available endpoints"
            },
            {
                "path": "/upload/",
                "method": "POST",
                "description": "Upload a video file"
            },
            {
                "path": "/process-audio/",
                "method": "POST",
                "description": "Extract and analyze speech from an uploaded video"
            },
            {
                "path": "/evaluate-speech/",
                "method": "POST",
                "description": "Evaluate speech transcript using LLM"
            }
        ],
        "version": "1.0"
    }

@app.post("/upload/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handles video upload and saves it to the server."""
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/process-audio/")
def process_audio(file_name: str):
    """Extracts and analyzes speech from uploaded video"""
    video_path = UPLOAD_DIR / file_name
    audio_path = extract_audio(video_path)

    # Run AI analysis
    analysis = SpeechAnalysisObject(audio_path)
    feedback = analysis.generate_feedback()
    
    return {
        "transcript": analysis.transcript,
        "sentiment": analysis.sentiment,
        "filler_words": analysis.filler_words,
        "emotion": analysis.emotion,
        "keywords": analysis.keywords,
        "pauses": analysis.pauses,
        "wpm": analysis.wpm,
        "clarity": analysis.clarity,
    }

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
    uvicorn.run(app, port=8000)
