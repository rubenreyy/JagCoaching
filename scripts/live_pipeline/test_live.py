import json
import numpy as np
import cv2
import time
from live_analysis_pipeline import run_analysis_once, run_loop
from audio_analysis import record_audio

def test_with_audio():
    """Test the pipeline with both video and audio"""
    print("Starting Presentation Coaching Analyzer with explicit audio recording...\n")
    print("Press Ctrl+C to stop.\n")
    
    try:
        cam = cv2.VideoCapture(0)
        while True:
            start = time.time()
            
            # Capture frame
            ret, frame = cam.read()
            if not ret:
                print("Failed to capture frame")
                continue
                
            # Record audio explicitly
            print("Recording 5 seconds of audio...")
            audio_data = record_audio(5)
            
            # Run analysis with both frame and audio
            result = run_analysis_once(frame, audio_data)
            print("\n Result:")
            print(json.dumps(result, indent=2))
            
            elapsed = time.time() - start
            time.sleep(max(0, 10 - elapsed))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        if 'cam' in locals():
            cam.release()

if __name__ == "__main__":
    print("Starting Presentation Coaching Analyzer...\n")
    print("Press Ctrl+C to stop.\n")
    
    # Choose which test to run
    # test_with_audio()  # Uncomment to test with explicit audio recording
    run_loop()  # Default test
