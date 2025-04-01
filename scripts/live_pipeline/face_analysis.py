import os
import cv2
import dlib
from imutils import face_utils
from deepface import DeepFace

# Construct full path to .dat file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

# Load dlib face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

def analyze_face(frame):
    emotion = detect_emotion(frame)
    eye_contact = detect_eye_contact(frame)
    return emotion, eye_contact

def detect_emotion(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        print(f"[FACE] Emotion error: {e}")
        return "unknown"

def detect_eye_contact(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        return "no_face"

    for face in faces:
        shape = predictor(gray, face)
        shape_np = face_utils.shape_to_np(shape)

        left_eye_pts = shape_np[36:42]
        right_eye_pts = shape_np[42:48]

        left_eye_center = left_eye_pts.mean(axis=0)
        right_eye_center = right_eye_pts.mean(axis=0)
        eye_avg_x = (left_eye_center[0] + right_eye_center[0]) / 2
        frame_center_x = frame.shape[1] / 2

        if abs(eye_avg_x - frame_center_x) < frame.shape[1] * 0.2:
            return "yes"
        else:
            return "no"

    return "unknown"