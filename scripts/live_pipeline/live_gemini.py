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
            eye_contact_feedback = "Great eye contact! You're connecting well with your audience."
        elif eye_contact == "limited":
            eye_contact_feedback = "Look directly at the camera to better connect with your audience."
        else:
            eye_contact_feedback = "Try to maintain consistent eye contact with the camera."
            
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
