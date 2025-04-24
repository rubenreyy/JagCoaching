import os
import json
from pptx import Presentation
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=".env.development")

# Configure Gemini API
gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash") 

def extract_presentation_content(file_path):
    """Extract text and other content from a PowerPoint presentation."""
    logger.info(f"Extracting content from presentation: {file_path}")
    presentation = Presentation(file_path)
    slides_content = []

    for slide_number, slide in enumerate(presentation.slides, start=1):
        slide_data = {"slide_number": slide_number, "text": [], "images": 0}

        # Extract text from slide
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    slide_data["text"].append(paragraph.text)

        # Count images
        slide_data["images"] = len([shape for shape in slide.shapes if shape.shape_type == 13])  # 13 = Picture

        slides_content.append(slide_data)

    logger.info(f"Extracted content from {len(slides_content)} slides.")
    return slides_content

def analyze_presentation_with_gemini(slides_content):
    """Send extracted content to Gemini for analysis."""
    logger.info("Preparing prompt for Gemini API...")
    prompt = f"""
You are an expert presentation coach. Analyze the following PowerPoint presentation and provide feedback on:
1. Slide content clarity
2. Visual design quality
3. Key topics and themes
4. Suggestions for improvement

Slides:
{json.dumps(slides_content, indent=2)}

Provide actionable insights in JSON format.
"""
    try:
        logger.info("Sending request to Gemini API...")
        response = model.generate_content(prompt)
        logger.info("Received response from Gemini API.")
        response_text = response.text

        # Parse the response as JSON
        try:
            result = json.loads(response_text)
            logger.info("Successfully parsed JSON response.")
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response. Returning raw text.")
            return {"raw_response": response_text}

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}")
        return {"error": str(e)}

def analyze_presentation(file_path):
    """Main function to analyze a PowerPoint presentation."""
    slides_content = extract_presentation_content(file_path)
    analysis_result = analyze_presentation_with_gemini(slides_content)
    return analysis_result

# Example Usage
if __name__ == "__main__":
    presentation_file = "C:/Users/Ruben/Documents/OneDrive/Documents/CS/Big Data/JagGradesPresentation.pptx"
    if os.path.exists(presentation_file):
        logger.info(f"Analyzing presentation: {presentation_file}")
        analysis_result = analyze_presentation(presentation_file)
        print(json.dumps(analysis_result, indent=4))
    else:
        logger.error(f"Presentation file not found: {presentation_file}")