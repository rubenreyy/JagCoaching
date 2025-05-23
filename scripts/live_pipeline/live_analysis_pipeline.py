import time
import cv2
import json
import threading
import logging
import numpy as np
from scripts.live_pipeline.face_analysis import analyze_face
from scripts.live_pipeline.audio_analysis import record_audio, transcribe_audio
from scripts.live_pipeline.live_gemini import get_gemini_feedback
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

# Shared results
face_result = {}
audio_result = {}

# Face analysis thread
def run_face_analysis(cam):
    global face_result
    ret, frame = cam.read()
    if ret:
        emotion, eye_contact, posture = analyze_face(frame)
        face_result = {"emotion": emotion, "eye_contact": eye_contact, "posture": posture}
    else:
        face_result = {"emotion": "unknown", "eye_contact": "unknown", "posture": "unknown"}

# Audio analysis thread
def run_audio_analysis():
    global audio_result
    audio = record_audio(10)
    transcript = transcribe_audio(audio)
    audio_result = {"transcript": transcript}

def run_analysis_once(frame, audio_data=None):
    """Run analysis on a single frame and optional audio data"""
    try:
        logger.info(f"Running analysis for frame and audio data")
        
        # Default values in case analysis fails
        emotion = "neutral"
        eye_contact = "limited"
        posture = "unknown"
        transcript = "No speech detected"
        audio_quality = "unknown"
        
        # Process frame if available
        if frame is not None:
            # Debug frame data type and size
            if isinstance(frame, str):
                logger.info(f"Frame is a string, length: {len(frame)}")
            elif isinstance(frame, np.ndarray):
                logger.info(f"Frame is numpy array, shape: {frame.shape}")
            else:
                logger.info(f"Frame is type: {type(frame)}")
            
            # Convert base64 string to numpy array if needed
            if isinstance(frame, str) and frame.startswith('data:image'):
                try:
                    # Extract the base64 part
                    import base64
                    from io import BytesIO
                    import re
                    
                    base64_data = re.sub('^data:image/.+;base64,', '', frame)
                    img_data = base64.b64decode(base64_data)
                    
                    # Convert to numpy array
                    nparr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    logger.info(f"Successfully converted base64 image to numpy array, shape: {frame.shape}")
                except Exception as e:
                    logger.error(f"Error converting base64 image: {e}")
                    frame = None
            
            # Run face analysis if we have a valid frame
            if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                emotion, eye_contact, posture = analyze_face(frame)
                logger.info(f"Face analysis results: emotion={emotion}, eye_contact={eye_contact}, posture={posture}")
            else:
                logger.warning("Invalid frame for face analysis")
        else:
            logger.warning("No frame provided for analysis")
        
        # Process audio if available
        if audio_data is not None:
            # Debug audio data type
            if isinstance(audio_data, str):
                logger.info(f"Audio data is a string, length: {len(audio_data)}")
            elif isinstance(audio_data, np.ndarray):
                logger.info(f"Audio data is numpy array, shape: {audio_data.shape}")
            else:
                logger.info(f"Audio data is type: {type(audio_data)}")
                
            # Transcribe audio
            transcript = transcribe_audio(audio_data)
            logger.info(f"Audio transcription: {transcript}")
            
            # Extract audio quality from transcript
            if "volume is low" in transcript:
                audio_quality = "low"
            elif "No speech detected" in transcript:
                audio_quality = "none"
            elif "Good volume" in transcript:
                audio_quality = "good"
            elif "Excellent" in transcript:
                audio_quality = "excellent"
            elif "too loud" in transcript:
                audio_quality = "too_loud"
            else:
                audio_quality = "moderate"
        else:
            logger.warning("No audio data provided for analysis")
            # Try to record audio directly if no audio data provided
            try:
                from scripts.live_pipeline.audio_analysis import record_audio
                logger.info("Attempting to record audio directly")
                audio_data = record_audio(3)  # Record 3 seconds
                if audio_data is not None:
                    transcript = transcribe_audio(audio_data)
                    logger.info(f"Recorded audio transcription: {transcript}")
                    
                    # Extract audio quality from transcript
                    if "volume is low" in transcript:
                        audio_quality = "low"
                    elif "No speech detected" in transcript:
                        audio_quality = "none"
                    elif "Good volume" in transcript:
                        audio_quality = "good"
                    elif "Excellent" in transcript:
                        audio_quality = "excellent"
                    elif "too loud" in transcript:
                        audio_quality = "too_loud"
                    else:
                        audio_quality = "moderate"
            except Exception as e:
                logger.error(f"Error recording audio: {e}")
                transcript = "No speech detected"
                audio_quality = "unknown"
        
        # Get Gemini feedback with posture information
        gemini_feedback = get_gemini_feedback(emotion, eye_contact, posture, transcript)
        
        return {
            "emotion": emotion,
            "eye_contact": eye_contact,
            "posture": posture,
            "transcript": transcript,
            "audio_quality": audio_quality,
            "gemini_feedback": gemini_feedback,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in run_analysis_once: {e}", exc_info=True)
        # Return fallback data in case of error
        return {
            "emotion": "neutral",
            "eye_contact": "limited",
            "posture": "unknown",
            "transcript": "Analysis in progress...",
            "audio_quality": "unknown",
            "gemini_feedback": {
                "posture_feedback": "Stand straight with shoulders back.",
                "expression_feedback": "Add more expression to engage your audience.",
                "eye_contact_feedback": "Look directly at the camera.",
                "voice_feedback": "Speak clearly and project your voice.",
                "overall_suggestion": "Continue practicing with more energy and expression."
            },
            "timestamp": datetime.now().isoformat()
        }

def run_loop():
    cam = cv2.VideoCapture(0)
    print(" Starting 10-second live feedback loop...\n")
    try:
        while True:
            start = time.time()
            ret, frame = cam.read()
            if ret:
                result = run_analysis_once(frame)
                print("\n Result:")
                print(json.dumps(result, indent=2))
            else:
                print("Failed to capture frame")

            elapsed = time.time() - start
            time.sleep(max(0, 10 - elapsed))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        cam.release()

if __name__ == "__main__":
    run_loop()
