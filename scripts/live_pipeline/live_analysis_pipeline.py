import time
import cv2
import json
import threading
from scripts.live_pipeline.face_analysis import analyze_face
from scripts.live_pipeline.audio_analysis import record_audio, transcribe_audio
from scripts.live_pipeline.live_gemini import get_gemini_feedback
from datetime import datetime
import logging

# Shared results
face_result = {}
audio_result = {}

# Face analysis thread
def run_face_analysis(cam):
    global face_result
    ret, frame = cam.read()
    if ret:
        emotion, eye_contact = analyze_face(frame)
        face_result = {"emotion": emotion, "eye_contact": eye_contact}
    else:
        face_result = {"emotion": "unknown", "eye_contact": "unknown"}

# Audio analysis thread
def run_audio_analysis():
    global audio_result
    audio = record_audio(10)
    transcript = transcribe_audio(audio)
    audio_result = {"transcript": transcript}

def run_analysis_once(frame):
    """Run analysis on a single frame"""
    try:
        # Run face analysis
        emotion, eye_contact = analyze_face(frame)
        
        # Run audio analysis (if audio data is available)
        transcript = ""  # This will be handled separately through the WebSocket
        
        # Get Gemini feedback
        gemini_data = get_gemini_feedback(emotion, eye_contact, transcript)
        
        return {
            "emotion": emotion,
            "eye_contact": eye_contact,
            "transcript": transcript,
            "gemini_feedback": gemini_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_loop():
    cam = cv2.VideoCapture(0)
    print(" Starting 10-second live feedback loop...\n")
    try:
        while True:
            start = time.time()
            result = run_analysis_once(cam)
            print("\n Result:")
            print(json.dumps(result, indent=2))

            elapsed = time.time() - start
            time.sleep(max(0, 10 - elapsed))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        cam.release()

if __name__ == "__main__":
    run_loop()
