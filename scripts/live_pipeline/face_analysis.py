import os
import cv2
import dlib
from imutils import face_utils
from deepface import DeepFace
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Construct full path to .dat file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

# Load dlib face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
try:
    if os.path.exists(predictor_path):
        predictor = dlib.shape_predictor(predictor_path)
        logger.info(f"Successfully loaded shape predictor from {predictor_path}")
    else:
        logger.warning(f"Shape predictor file not found at {predictor_path}")
        logger.warning("Eye contact detection will be limited")
        predictor = None
except Exception as e:
    logger.error(f"Error loading shape predictor: {e}")
    predictor = None

def analyze_face(frame):
    # Check if frame is valid
    if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
        logger.warning("[FACE] Invalid frame for analysis")
        return "neutral", "limited", "unknown"
        
    try:
        emotion = detect_emotion(frame)
        eye_contact = detect_eye_contact(frame)
        posture = detect_posture(frame)
        logger.info(f"Face analysis results: emotion={emotion}, eye_contact={eye_contact}, posture={posture}")
        return emotion, eye_contact, posture
    except Exception as e:
        logger.error(f"[FACE] Analysis error: {e}", exc_info=True)
        return "neutral", "limited", "unknown"

def detect_emotion(frame):
    try:
        # Check if frame is valid
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            logger.warning("[FACE] Invalid frame for emotion detection")
            return "neutral"
            
        # Use DeepFace for emotion detection with more robust settings
        result = DeepFace.analyze(
            frame, 
            actions=['emotion'], 
            enforce_detection=False,
            detector_backend='opencv'  # Use OpenCV for more reliable detection
        )
        
        if isinstance(result, list) and len(result) > 0:
            emotion = result[0]['dominant_emotion']
            emotion_scores = result[0]['emotion']
            # Log confidence scores for debugging
            logger.info(f"[FACE] Emotion confidence scores: {emotion_scores}")
            
            # Add more nuanced emotion detection with confidence thresholds
            if emotion_scores['happy'] > 50:
                emotion = 'happy'
                logger.info("[FACE] Detected clear smile/happiness")
            elif emotion_scores['sad'] > 40 or emotion_scores['disgust'] > 40:
                emotion = 'sad'  # Combine sad and disgust as "frowning"
                logger.info("[FACE] Detected frown/negative expression")
            elif emotion_scores['neutral'] > 80:
                emotion = 'neutral'
                logger.info("[FACE] Detected very neutral expression - could use more expressiveness")
            elif emotion_scores['surprise'] > 40:
                emotion = 'surprise'
                logger.info("[FACE] Detected surprised expression")
        else:
            emotion = result['dominant_emotion']
            emotion_scores = result['emotion']
            # Log confidence scores for debugging
            logger.info(f"[FACE] Emotion confidence scores: {emotion_scores}")
            
            # Same nuanced detection for non-list result
            if emotion_scores['happy'] > 50:
                emotion = 'happy'
                logger.info("[FACE] Detected clear smile/happiness")
            elif emotion_scores['sad'] > 40 or emotion_scores['disgust'] > 40:
                emotion = 'sad'  # Combine sad and disgust as "frowning"
                logger.info("[FACE] Detected frown/negative expression")
            elif emotion_scores['neutral'] > 80:
                emotion = 'neutral'
                logger.info("[FACE] Detected very neutral expression - could use more expressiveness")
            elif emotion_scores['surprise'] > 40:
                emotion = 'surprise'
                logger.info("[FACE] Detected surprised expression")
            
        logger.info(f"[FACE] Detected emotion: {emotion}")
        return emotion
    except Exception as e:
        logger.error(f"[FACE] Emotion detection error: {e}")
        return "neutral"  # Return a default emotion

def detect_eye_contact(frame):
    # If predictor is not available, return a default value
    if predictor is None:
        logger.warning("[FACE] Shape predictor not available, using default eye contact value")
        return "limited"
        
    try:
        # Check if frame is valid
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            logger.warning("[FACE] Invalid frame for eye contact detection")
            return "limited"
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Improve face detection by adjusting parameters
        faces = detector(gray, 1)
        
        if len(faces) == 0:
            # Try with different parameters if no face detected initially
            faces = detector(gray, 2)
            
            if len(faces) == 0:
                # Try with OpenCV's face detector as a fallback
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                opencv_faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                
                if len(opencv_faces) == 0:
                    logger.info("[FACE] No face detected in frame with any method")
                    return "limited"
                else:
                    # Convert OpenCV face to dlib rectangle
                    dlib_faces = []
                    for (x, y, w, h) in opencv_faces:
                        dlib_faces.append(dlib.rectangle(x, y, x+w, y+h))
                    faces = dlib_faces

        # Process the detected faces
        for face in faces:
            shape = predictor(gray, face)
            shape_np = face_utils.shape_to_np(shape)

            # Get eye landmarks
            left_eye_pts = shape_np[36:42]
            right_eye_pts = shape_np[42:48]
            
            # Calculate eye aspect ratio (EAR) to detect if eyes are open
            def eye_aspect_ratio(eye):
                A = np.linalg.norm(eye[1] - eye[5])
                B = np.linalg.norm(eye[2] - eye[4])
                C = np.linalg.norm(eye[0] - eye[3])
                ear = (A + B) / (2.0 * C)
                return ear
                
            left_ear = eye_aspect_ratio(left_eye_pts)
            right_ear = eye_aspect_ratio(right_eye_pts)
            
            # If eyes are mostly closed, likely not making eye contact
            if left_ear < 0.2 and right_ear < 0.2:
                logger.info("[FACE] Eyes appear closed, limited eye contact")
                return "limited"
            
            # Calculate eye centers
            left_eye_center = left_eye_pts.mean(axis=0).astype("int")
            right_eye_center = right_eye_pts.mean(axis=0).astype("int")
            
            # Calculate face center
            face_center_x = (face.left() + face.right()) // 2
            face_center_y = (face.top() + face.bottom()) // 2
            
            # FIXED: Corrected logic for eye contact detection
            # When looking at camera, eyes should be more centered in the face
            left_eye_offset = abs(left_eye_center[0] - face_center_x)
            right_eye_offset = abs(right_eye_center[0] - face_center_x)
            vertical_offset = abs((left_eye_center[1] + right_eye_center[1])/2 - face_center_y)
            
            # Adjusted thresholds and corrected logic
            # When looking directly at camera, offsets should be SMALLER
            if left_eye_offset < 25 and right_eye_offset < 25 and vertical_offset < 35:
                logger.info("[FACE] Good eye contact detected - eyes centered")
                return "yes"
            else:
                logger.info("[FACE] Limited eye contact detected - eyes not centered")
                return "limited"
            
    except Exception as e:
        logger.error(f"[FACE] Eye contact detection error: {e}", exc_info=True)
        return "limited"

def detect_posture(frame):
    """Detect posture based on face and shoulder position"""
    try:
        # Check if frame is valid
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            logger.warning("[FACE] Invalid frame for posture detection")
            return "unknown"
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = detector(gray, 1)
        
        if len(faces) == 0:
            logger.info("[FACE] No face detected for posture analysis")
            return "unknown"
            
        # Get the first face
        face = faces[0]
        
        # Get face dimensions and position
        face_height = face.bottom() - face.top()
        face_width = face.right() - face.left()
        face_center_y = (face.top() + face.bottom()) // 2
        
        # Get frame dimensions
        frame_height, frame_width = frame.shape[:2]
        
        # Check vertical position of face in frame
        # If face is too low in frame, likely slouching
        vertical_position = face_center_y / frame_height
        
        if vertical_position > 0.6:  # Face is in lower part of frame
            logger.info("[FACE] Poor posture detected - face too low in frame")
            return "poor"
        
        # Check face tilt using landmarks if available
        if predictor is not None:
            shape = predictor(gray, face)
            shape_np = face_utils.shape_to_np(shape)
            
            # Get nose tip and chin
            nose_tip = shape_np[30]
            chin = shape_np[8]
            
            # Calculate angle of face tilt
            angle = np.degrees(np.arctan2(chin[1] - nose_tip[1], chin[0] - nose_tip[0]))
            
            # If face is tilted too much, likely poor posture
            if abs(angle - 90) > 15:
                logger.info(f"[FACE] Poor posture detected - face tilted at {angle} degrees")
                return "poor"
        
        logger.info("[FACE] Good posture detected")
        return "good"
        
    except Exception as e:
        logger.error(f"[FACE] Posture detection error: {e}", exc_info=True)
        return "unknown"