import cv2
import numpy as np
import sounddevice as sd
import time
import matplotlib.pyplot as plt
from scripts.live_pipeline.face_analysis import analyze_face
from scripts.live_pipeline.audio_analysis import transcribe_audio

def test_camera():
    """Test camera capture and face analysis"""
    print("Testing camera capture...")
    
    # Open camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("ERROR: Could not open camera!")
        return False
    
    # Capture frame
    ret, frame = cam.read()
    if not ret:
        print("ERROR: Could not read frame from camera!")
        cam.release()
        return False
    
    # Display frame size
    print(f"Frame captured successfully! Size: {frame.shape}")
    
    # Test face analysis
    print("Running face analysis...")
    emotion, eye_contact = analyze_face(frame)
    print(f"Face analysis results: emotion={emotion}, eye_contact={eye_contact}")
    
    # Release camera
    cam.release()
    return True

def test_audio():
    """Test audio recording and transcription"""
    print("Testing audio recording...")
    
    # Record parameters
    duration = 5  # seconds
    sample_rate = 16000
    
    print(f"Recording {duration} seconds of audio. Please speak into your microphone...")
    
    # Record audio
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    
    # Convert to 1D array
    audio_data = audio_data.flatten()
    
    # Display audio info
    print(f"Audio recorded successfully! Shape: {audio_data.shape}, Max amplitude: {np.max(np.abs(audio_data))}")
    
    # Plot audio waveform
    plt.figure(figsize=(10, 4))
    plt.plot(audio_data)
    plt.title("Audio Waveform")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.savefig("audio_waveform.png")
    print("Audio waveform saved to audio_waveform.png")
    
    # Test transcription
    print("Running audio transcription...")
    transcript = transcribe_audio(audio_data)
    print(f"Transcription result: '{transcript}'")
    
    return True

if __name__ == "__main__":
    print("=== Testing Camera and Audio ===")
    
    camera_ok = test_camera()
    print("\n" + "="*30 + "\n")
    
    audio_ok = test_audio()
    
    print("\n=== Test Results ===")
    print(f"Camera: {'OK' if camera_ok else 'FAILED'}")
    print(f"Audio: {'OK' if audio_ok else 'FAILED'}") 