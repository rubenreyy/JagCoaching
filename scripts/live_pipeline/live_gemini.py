import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.development")

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-001")

def get_gemini_feedback(emotion, eye_contact, transcript):
    prompt = f"""
You are an expert speech coach. Provide a detailed feedback report based on the following analysis:

The following is a 10-second segment from a speaker:
- Detected facial emotion: {emotion}
- Eye contact: {eye_contact}
- Transcribed speech: "{transcript}"
"""

    response = model.generate_content(
        contents=prompt,
        generation_config={
            "response_mime_type": "application/json",
            "stop_sequences": ["\n\n"]
        }
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        print("[ERROR] Failed to parse Gemini response as JSON:", e)
        return {"feedback": response.text}
