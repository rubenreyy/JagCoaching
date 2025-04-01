import time
import cv2
import json
import threading
from face_analysis import analyze_face
from audio_analysis import record_audio, transcribe_audio
from live_gemini import get_gemini_feedback

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

def run_analysis_once(cam):
    global face_result, audio_result
    face_result = {}
    audio_result = {}

    face_thread = threading.Thread(target=run_face_analysis, args=(cam,))
    audio_thread = threading.Thread(target=run_audio_analysis)

    face_thread.start()
    audio_thread.start()

    face_thread.join()
    audio_thread.join()

    emotion = face_result.get("emotion", "unknown")
    eye_contact = face_result.get("eye_contact", "unknown")
    transcript = audio_result.get("transcript", "")

    gemini_data = get_gemini_feedback(emotion, eye_contact, transcript)

    return {
        "emotion": emotion,
        "eye_contact": eye_contact,
        "transcript": transcript,
        "gemini_feedback": gemini_data
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
