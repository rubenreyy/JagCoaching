import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Set up logger
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=".env.development")

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")  # Updated model name

def get_gemini_feedback(emotion, eye_contact, posture, transcript):
    logger.info(f"[GEMINI] Getting feedback for: emotion={emotion}, eye_contact={eye_contact}, posture={posture}, transcript={transcript}")
    
    # Determine if we have real data or defaults
    has_real_emotion = emotion != "neutral" and emotion != "unknown"
    has_real_eye_contact = eye_contact != "unknown" 
    has_real_posture = posture != "unknown"
    has_real_transcript = transcript != "No speech detected" and "analysis" not in transcript.lower()
    
    # If we have mostly default values, provide more specific feedback based on what we do have
    if not (has_real_transcript):
        # Create feedback based on emotion, eye contact, and posture
        if emotion == "happy":
            expression_feedback = "Your smile projects confidence and warmth. Maintain this positive energy."
        elif emotion == "sad":
            expression_feedback = "Your expression appears downcast. Lift your face and try to project more enthusiasm."
        elif emotion == "angry":
            expression_feedback = "Your expression appears tense. Relax your facial muscles and soften your look."
        elif emotion == "fear":
            expression_feedback = "You appear nervous. Take a deep breath and relax your facial muscles."
        elif emotion == "surprise":
            expression_feedback = "Your surprised expression shows engagement. Use this to emphasize key points."
        elif emotion == "disgust":
            expression_feedback = "Your expression may appear negative. Aim for a more neutral or positive look."
        else:
            expression_feedback = "Try to vary your expressions to engage your audience better."
            
        if eye_contact == "yes":
            eye_contact_feedback = "Excellent eye contact! You're connecting well with your audience."
        elif eye_contact == "limited":
            eye_contact_feedback = "Try looking directly at the camera lens more consistently. Position yourself so your eyes are level with the camera."
        else:
            eye_contact_feedback = "Try to maintain consistent eye contact with the camera lens."
            
        if posture == "good":
            posture_feedback = "Your posture is excellent. You appear confident and engaged."
        elif posture == "poor":
            posture_feedback = "Stand taller with shoulders back and chin up to project confidence."
        else:
            posture_feedback = "Stand tall with shoulders back and chin parallel to the floor."
            
        # Improved voice feedback based on transcript
        if "too quiet" in transcript.lower():
            voice_feedback = "Speak louder to ensure your audience can hear you clearly."
        elif "volume is low" in transcript.lower():
            voice_feedback = "Project your voice more to reach the back of the room."
        elif "good volume" in transcript.lower():
            voice_feedback = "Good volume. Maintain this level of projection."
        elif "excellent projection" in transcript.lower():
            voice_feedback = "Excellent voice projection. Your audience can hear you clearly."
        else:
            voice_feedback = "Speak clearly with varied tone and appropriate volume."
            
        return {
            "posture_feedback": posture_feedback,
            "expression_feedback": expression_feedback,
            "eye_contact_feedback": eye_contact_feedback,
            "voice_feedback": voice_feedback,
            "overall_suggestion": "Focus on connecting with your audience through expressions and eye contact."
        }
    
    prompt = f"""
You are an expert speech coach providing BRIEF, CONCISE feedback. Keep each feedback point to 1-2 short sentences maximum.

Analyze this 10-second segment:
- Facial emotion: {emotion}
- Eye contact: {eye_contact}
- Posture: {posture}
- Speech: "{transcript}"

Be direct and actionable. For posture, assume the speaker is standing and suggest "Stand with shoulders back, spine straight."

Provide your feedback in JSON format with the following structure:
{{
  "posture_feedback": "Very brief feedback about posture (max 15 words)",
  "expression_feedback": "Very brief feedback about facial expressions (max 15 words)",
  "eye_contact_feedback": "Very brief feedback about eye contact (max 15 words)",
  "voice_feedback": "Very brief feedback about voice (max 15 words)",
  "overall_suggestion": "One concise improvement tip (max 20 words)"
}}

Remember: Be extremely concise. No explanations needed.
"""
    
    try:
        logger.info("[GEMINI] Sending request to Gemini API...")
        response = model.generate_content(prompt)
        logger.info("[GEMINI] Received response from Gemini API")
        
        response_text = response.text
        # Try to parse as JSON directly
        try:
            result = json.loads(response_text)
            logger.info("[GEMINI] Successfully parsed JSON response")
            return result
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code block
            if "```json" in response_text and "```" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_text)
                logger.info("[GEMINI] Successfully extracted JSON from markdown")
                return result
            else:
                raise Exception("Could not extract JSON from response")
    except Exception as e:
        logger.error(f"[GEMINI] Failed to get Gemini response: {e}")
        return {
            "posture_feedback": "Stand straight and face forward.",
            "expression_feedback": f"Current emotion: {emotion}. Add more expression.",
            "eye_contact_feedback": f"Eye contact: {eye_contact}. Look at camera.",
            "voice_feedback": f"Speech detected: {transcript or 'None'}. Speak clearly.",
            "overall_suggestion": "Engage more with your audience."
        }

# Add a new function to generate session summaries
def get_session_summary(metrics):
    """Generate a comprehensive session summary based on collected metrics"""
    logger.info(f"[GEMINI] Generating session summary from metrics: {metrics}")
    
    summary = {}
    
    # Eye contact summary
    eye_contact = metrics.get("eye_contact", {})
    eye_contact_total = eye_contact.get("total", 0)
    eye_contact_good = eye_contact.get("yes", 0)
    
    if eye_contact_total > 0:
        eye_contact_ratio = eye_contact_good / eye_contact_total
        
        if eye_contact_ratio >= 0.7:
            eye_contact_feedback = "Excellent eye contact throughout your session. You consistently engaged with the camera."
        elif eye_contact_ratio >= 0.4:
            eye_contact_feedback = "Your eye contact was inconsistent. Try to maintain more consistent eye contact with the camera."
        else:
            eye_contact_feedback = "Your eye contact needs improvement. Practice looking directly at the camera lens more consistently."
    else:
        eye_contact_feedback = "No eye contact data available for this session."
    
    # Emotion summary
    emotion = metrics.get("emotion", {})
    emotion_total = emotion.get("total", 0)
    emotion_happy = emotion.get("happy", 0)
    emotion_neutral = emotion.get("neutral", 0)
    
    if emotion_total > 0:
        emotion_positive_ratio = emotion_happy / emotion_total
        emotion_neutral_ratio = emotion_neutral / emotion_total
        
        if emotion_positive_ratio >= 0.6:
            emotion_feedback = "Great facial expressions! You showed positive engagement throughout your presentation."
        elif emotion_neutral_ratio >= 0.7:
            emotion_feedback = "Your expressions were mostly neutral. Try to add more varied expressions to engage your audience."
        else:
            emotion_feedback = "Your expressions could use improvement. Practice showing more positive and engaging expressions."
    else:
        emotion_feedback = "No expression data available for this session."
    
    # Posture summary
    posture = metrics.get("posture", {})
    posture_total = posture.get("total", 0)
    posture_good = posture.get("good", 0)
    
    if posture_total > 0:
        posture_ratio = posture_good / posture_total
        
        if posture_ratio >= 0.7:
            posture_feedback = "Excellent posture throughout your presentation. You appeared confident and professional."
        elif posture_ratio >= 0.4:
            posture_feedback = "Your posture was inconsistent. Remember to maintain good posture throughout your presentation."
        else:
            posture_feedback = "Your posture needs improvement. Practice standing/sitting straight with shoulders back."
    else:
        posture_feedback = "No posture data available for this session."
    
    # Audio quality summary
    audio = metrics.get("audio_quality", {})
    audio_total = audio.get("total", 0)
    audio_good = audio.get("good", 0) + audio.get("excellent", 0)
    
    if audio_total > 0:
        audio_ratio = audio_good / audio_total
        
        if audio_ratio >= 0.7:
            audio_feedback = "Excellent voice projection and clarity throughout your presentation."
        elif audio_ratio >= 0.4:
            audio_feedback = "Your voice projection was inconsistent. Practice maintaining consistent volume and clarity."
        else:
            audio_feedback = "Your voice projection needs improvement. Practice speaking louder and more clearly."
    else:
        audio_feedback = "No audio quality data available for this session."
    
    # Overall assessment
    overall_scores = []
    if eye_contact_total > 0:
        overall_scores.append(eye_contact_ratio)
    if emotion_total > 0:
        overall_scores.append(emotion_positive_ratio)
    if posture_total > 0:
        overall_scores.append(posture_ratio)
    if audio_total > 0:
        overall_scores.append(audio_ratio)
    
    if overall_scores:
        overall_score = sum(overall_scores) / len(overall_scores)
        
        if overall_score >= 0.7:
            overall_feedback = "Great job! You demonstrated strong presentation skills overall. Keep up the good work!"
        elif overall_score >= 0.4:
            overall_feedback = "Your presentation skills are developing well. Focus on consistency in all areas for improvement."
        else:
            overall_feedback = "Your presentation skills need more practice. Focus on the specific areas highlighted for improvement."
    else:
        overall_feedback = "Not enough data to provide an overall assessment."
    
    return {
        "eye_contact_feedback": eye_contact_feedback,
        "expression_feedback": emotion_feedback,
        "posture_feedback": posture_feedback,
        "voice_feedback": audio_feedback,
        "overall_suggestion": overall_feedback
    }
