import os
import functools
from time import time
import numpy as np
import torch
import librosa
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from keybert import KeyBERT
from scipy.signal import find_peaks
import google.generativeai as genai
from google.genai import types
from dotenv import load_dotenv
import logging
import re

# Configure disk space use
os.environ["XDG_CACHE_HOME"] = "/mnt/disk-6/.cache"
os.environ["TRANSFORMERS_CACHE"] = "/mnt/disk-6/.hf_cache"

# Load environment variables
load_dotenv("./.env.development")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine compute device
device = "cuda:0" if torch.cuda.is_available() else "cpu"

@functools.lru_cache(maxsize=40)
def load_librosa(audio_path):
    try:
        audio, sr = librosa.load(audio_path, sr=16000, duration=300)
    except Exception as e:
        logger.error(f"Error loading audio file {audio_path}: {e}")
        return None, None
    return audio, sr


def transcribe_speech(audio_path):
    import whisper
    try:
        logger.info(f"Starting transcription for {audio_path}")
        model = whisper.load_model("small")
        logger.info("Whisper model loaded successfully")
        result = model.transcribe(audio_path, language="en", task="transcribe", verbose=False)
        
        # Enhanced post-processing of transcription
        text = result["text"].strip()
        logger.info(f"Raw transcription: {text[:100]}...")
        
        # Remove any non-speech artifacts and standardize spacing
        text = re.sub(r'\s+', ' ', text)
        
        # Log information about the transcription
        word_count = len(text.split())
        logger.info(f"Transcription complete: {word_count} words")
        
        if word_count == 0:
            logger.warning("Transcription produced no words!")
            return "No speech detected. Please check audio quality."
            
        return text
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise


def analyze_sentiment(text):
    try:
        # Check for empty or very short text
        if not text or len(text.strip()) < 10:
            logger.warning("Text too short for sentiment analysis")
            return {
                "label": "Neutral",
                "score": 0.5,
                "suggestion": "Text too short for sentiment analysis."
            }
            
        # Limit text size to prevent model issues
        analysis_text = text[:1024] if len(text) > 1024 else text
        
        # Log steps for debugging
        logger.info(f"Starting sentiment analysis on text (length: {len(analysis_text)})")
        
        # Using a more reliable sentiment model from Hugging Face
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        
        # Move model to specific device with error handling
        try:
            if device != "cpu":
                model = model.to(device)
                logger.info(f"Sentiment model moved to {device}")
            else:
                logger.info("Using CPU for sentiment analysis")
        except Exception as device_err:
            logger.warning(f"Device error, falling back to CPU: {device_err}")
            model = model.to("cpu")
            
        # Run inference with direct model control
        inputs = tokenizer(analysis_text, return_tensors="pt", truncation=True, max_length=512)
        if device != "cpu":
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
        with torch.no_grad():
            outputs = model(**inputs)
            
        # Process scores
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        positive_score = scores[0][1].item()
        
        # Map the result to expected format with more detailed analysis
        if positive_score > 0.75:
            label = "Very Positive"
            suggestion = "Your strong positive tone helps engage the audience."
        elif positive_score > 0.55:
            label = "Positive"
            suggestion = "Your positive tone is good for audience engagement."
        elif positive_score < 0.35:
            label = "Negative"
            suggestion = "Consider maintaining a more positive or neutral tone."
        elif positive_score < 0.45:
            label = "Slightly Negative"
            suggestion = "Your tone leans slightly negative. Consider a more neutral approach."
        else:
            label = "Neutral"
            suggestion = "Your tone is well-balanced and professional."
            
        logger.info(f"Sentiment analysis complete: {label} ({positive_score:.2f})")
        return {
            "label": label,
            "score": positive_score,
            "suggestion": suggestion
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}", exc_info=True)
        # Return fallback result if sentiment analysis fails
        return {
            "label": "Neutral",
            "score": 0.5,
            "suggestion": "Unable to analyze sentiment accurately. Consider reviewing the tone yourself."
        }


def detect_filler_words(text):
    fillers = ["uh", "um", "like", "you know", "so", "actually", "basically"]
    word_list = text.lower().split()
    filler_count = {word: word_list.count(word) for word in fillers if word in word_list}
    total_fillers = sum(filler_count.values())
    assessment = {
        "counts": filler_count,
        "total": total_fillers,
        "suggestion": (
            "Great job minimizing filler words!" if total_fillers <= 2
            else "Try to reduce filler words by pausing briefly instead."
        )
    }
    return assessment


def analyze_emotion(audio_path):
    try:
        emotion_pipeline = pipeline("audio-classification", model="superb/hubert-large-superb-er", device=device)
        return emotion_pipeline(audio_path)
    except Exception as e:
        logger.error(f"Emotion analysis failed: {str(e)}", exc_info=True)
        # Return fallback result if emotion analysis fails
        return [{"label": "neutral", "score": 1.0}]


def extract_keywords(text):
    try:
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
        return [kw[0] for kw in keywords]
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}", exc_info=True)
        # Return fallback result
        return ["speech", "analysis"]


def detect_pauses(audio_path):
    try:
        audio, sr = load_librosa(audio_path)
        if audio is None or sr is None:
            return 0
        energy = librosa.feature.rms(y=audio)[0]
        peaks, _ = find_peaks(-energy, distance=sr//2, height=-np.mean(energy))
        return len(peaks)
    except Exception as e:
        logger.error(f"Pause detection failed: {str(e)}", exc_info=True)
        return 0


def analyze_speech_rate(transcript, audio_path):
    try:
        audio, sr = load_librosa(audio_path)
        if audio is None or sr is None:
            return {"wpm": 0, "assessment": "unknown", "suggestion": "Unable to analyze speech rate."}
        duration = librosa.get_duration(y=audio, sr=sr)
        word_count = len(transcript.split())
        wpm = (word_count / duration) * 60
        return {
            "wpm": round(wpm, 2),
            "assessment": "optimal" if 120 <= wpm <= 150 else "too slow" if wpm < 120 else "too fast",
            "suggestion": (
                "Your speaking pace is ideal for clear communication." if 120 <= wpm <= 150
                else "Consider speaking a bit faster to maintain engagement." if wpm < 120
                else "Try slowing down slightly for better clarity."
            )
        }
    except Exception as e:
        logger.error(f"Speech rate analysis failed: {str(e)}", exc_info=True)
        return {"wpm": 0, "assessment": "unknown", "suggestion": "Unable to analyze speech rate."}


def grammar_correction(text):
    try:
        grammar_pipeline = pipeline("text2text-generation", model="grammarly/coedit-large", device=device)
        corrected_text = grammar_pipeline(text, max_length=512)[0]['generated_text']
        return corrected_text
    except Exception as e:
        logger.error(f"Grammar correction failed: {str(e)}", exc_info=True)
        return text  # Return original text if correction fails


def analyze_monotone_speech(audio_path):
    try:
        audio, sr = load_librosa(audio_path)
        if audio is None or sr is None:
            return "Unknown"
        pitch, _ = librosa.piptrack(y=audio, sr=sr)
        pitch = pitch[pitch > 0]
        if len(pitch) == 0:  # Handle case with no detected pitch
            return "Unknown"
        pitch_variance = np.var(pitch)
        return "Monotone" if pitch_variance < 500 else "Dynamic"
    except Exception as e:
        logger.error(f"Monotone speech analysis failed: {str(e)}", exc_info=True)
        return "Unknown"


# Fixed pronunciation clarity evaluation
def evaluate_pronunciation_clarity(audio_path, transcript=None):
    try:
        # If no transcript is provided, use a fallback value
        if transcript is None or not transcript or transcript == "No speech detected. Please check audio quality.":
            logger.warning("No transcript provided for clarity evaluation, using fallback value")
            return 60.0  # Default reasonable value
            
        # Initialize ASR model
        asr_pipeline = pipeline(
            "automatic-speech-recognition", 
            model="facebook/wav2vec2-base-960h", 
            device=device
        )
        
        # Get ASR transcription
        asr_result = asr_pipeline(audio_path)
        asr_transcription = asr_result["text"].strip()
        
        logger.info(f"ASR transcription: {asr_transcription[:100]}...")
        
        # Calculate word count
        asr_words = asr_transcription.split()
        expected_words = transcript.split()
        
        if len(asr_words) == 0 or len(expected_words) == 0:
            logger.warning("Empty transcription detected")
            return 50.0  # Default middle value if can't analyze
        
        # Calculate word error rate (simplified)
        # For a more detailed WER, we would use the Levenshtein distance
        matched_words = sum(1 for w in asr_words if w.lower() in [ew.lower() for ew in expected_words])
        total_words = len(expected_words)
        
        # Calculate clarity score (higher is better)
        clarity_score = min((matched_words / total_words) * 100, 100.0)
        
        # Get audio quality metrics
        audio, sr = load_librosa(audio_path)
        if audio is not None and sr is not None:
            # Calculate signal-to-noise ratio (simplified)
            signal_power = np.mean(audio**2)
            noise_estimation = np.mean(np.sort(audio**2)[:int(len(audio)*0.1)])  # Use lowest 10% as noise
            if noise_estimation > 0:
                snr = 10 * np.log10(signal_power / noise_estimation)
                
                # Adjust clarity score based on SNR
                snr_factor = max(min(snr / 20, 1.0), 0.0)  # Normalize SNR to [0,1]
                clarity_score = clarity_score * (0.7 + 0.3 * snr_factor)
        
        # Ensure we get a reasonable score between 10 and 100
        clarity_score = max(min(clarity_score, 100.0), 10.0)
        
        # Log clarity analysis details
        logger.info(f"Clarity analysis completed: {clarity_score:.2f}%")
        logger.info(f"ASR word count: {len(asr_words)}, Expected word count: {len(expected_words)}")
        
        return round(clarity_score, 2)
    except Exception as e:
        logger.error(f"Pronunciation clarity evaluation failed: {str(e)}", exc_info=True)
        return 60.0  # Default reasonable value if calculation fails


def generate_feedback(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity):
    feedback = "Speech Feedback Report:\n"
    feedback += f"\nTranscription: {transcript[:200]}..."
    feedback += f"\n\nSentiment: {sentiment['label']} ({sentiment['score']:.2f})"
    feedback += f"\nDetected Filler Words: {filler_words}"
    feedback += f"\nEmotions: {emotion[0]['label']} ({emotion[0]['score']:.2f})"
    feedback += f"\nKey Topics: {', '.join(keywords)}"
    feedback += f"\nNumber of Significant Pauses: {pauses}"
    feedback += f"\nSpeech Rate: {wpm['wpm']} words per minute"
    feedback += f"\nGrammar Corrections: {corrected_text}"
    feedback += f"\nSpeech Tone: {monotone}"
    
    # Enhanced clarity reporting
    clarity_assessment = (
        "Excellent clarity" if clarity >= 90 else
        "Good clarity" if clarity >= 75 else
        "Average clarity" if clarity >= 60 else
        "Below average clarity" if clarity >= 40 else
        "Poor clarity"
    )
    
    feedback += f"\nPronunciation Clarity: {clarity}% - {clarity_assessment}"
    return feedback


def generate_smart_report(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity):
    # Enhanced clarity assessment for the report
    clarity_assessment = (
        "Excellent clarity" if clarity >= 90 else
        "Good clarity" if clarity >= 75 else
        "Average clarity" if clarity >= 60 else
        "Below average clarity" if clarity >= 40 else
        "Poor clarity"
    )
    
    prompt = f"""
    1. Transcription: {transcript}
    2. Sentiment: {sentiment}
    3. Filler Words: {filler_words}
    4. Emotions: {emotion}
    5. Key Topics: {keywords}
    6. Significant Pauses: {pauses}
    7. Speech Rate: {wpm['wpm']} words per minute
    8. Grammar Corrections: {corrected_text}
    9. Speech Tone: {monotone}
    10. Pronunciation Clarity: {clarity}% - {clarity_assessment}
    Provide actionable insights and suggestions for improvement.
    """
    try:
        api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            logger.error("Google Gemini API key not found in environment variables")
            return "Error: API key not found for smart report generation."
            
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction="You are an expert speech coach. Provide a detailed feedback report based on the following analysis",
                response_mime_type="application/json",
                stop_sequences=["\n\n"],
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Smart report generation failed: {e}")
        return "Error generating smart report. Please check API key and connection."


def main():
    try:
        audio_file = "scripts/tests/Student_1.wav"
        logger.info(f"Starting analysis for {audio_file}")
        
        # Check if file exists
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            print(f"Error: Audio file not found at {audio_file}")
            return
            
        transcript = transcribe_speech(audio_file)
        logger.info("Transcription complete")
        
        sentiment = analyze_sentiment(transcript)
        logger.info("Sentiment analysis complete")
        
        filler_words = detect_filler_words(transcript)
        logger.info("Filler word detection complete")
        
        emotion = analyze_emotion(audio_file)
        logger.info("Emotion analysis complete")
        
        keywords = extract_keywords(transcript)
        logger.info("Keyword extraction complete")
        
        pauses = detect_pauses(audio_file)
        logger.info("Pause detection complete")
        
        wpm = analyze_speech_rate(transcript, audio_file)
        logger.info("Speech rate analysis complete")
        
        corrected_text = grammar_correction(transcript)
        logger.info("Grammar correction complete")
        
        monotone = analyze_monotone_speech(audio_file)
        logger.info("Monotone speech analysis complete")
        
        # Pass the transcript to the clarity evaluation function
        clarity = evaluate_pronunciation_clarity(audio_file, transcript)
        logger.info(f"Pronunciation clarity evaluation complete: {clarity}%")

        feedback_report = generate_feedback(
            transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity
        )
        print(feedback_report)
        logger.info("Feedback report generated")

        smart_report = generate_smart_report(
            transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity
        )
        print(smart_report)
        logger.info("Smart report generated")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        print(f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    start_time = time()
    main()
    execution_time = time() - start_time
    print(f"Execution time: {execution_time:.2f} seconds")
    logger.info(f"Execution completed in {execution_time:.2f} seconds")