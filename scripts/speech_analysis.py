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
        model = whisper.load_model("medium")
        logger.info("Whisper model loaded successfully")
        result = model.transcribe(audio_path, language="en", task="transcribe", verbose=False)
        return result["text"]
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise


# Updated to use a more reliable sentiment model
def analyze_sentiment(text):
    try:
        # Using a more reliable sentiment model from Hugging Face
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=device if device != "cpu" else -1  # -1 for CPU
        )
        result = sentiment_pipeline(text)[0]
        
        # Map the result to your expected format
        score = result["score"]
        if result["label"] == "POSITIVE":
            label = "Positive"
            suggestion = "Your positive tone helps engage the audience."
        elif result["label"] == "NEGATIVE":
            label = "Negative"
            suggestion = "Consider maintaining a more neutral tone."
        else:
            label = "Neutral"
            suggestion = "Your tone is well-balanced and professional."
            
        return {
            "label": label,
            "score": score,
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


def evaluate_pronunciation_clarity(audio_path):
    try:
        clarity_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h", device=device)
        transcription = clarity_pipeline(audio_path)["text"]
        total_words = len(transcription.split())
        if total_words == 0:  # Handle empty transcription
            return 0.0
        clarity_score = len([word for word in transcription.split() if word.isalpha()]) / total_words
        return round(clarity_score * 100, 2)
    except Exception as e:
        logger.error(f"Pronunciation clarity evaluation failed: {str(e)}", exc_info=True)
        return 0.0


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
    feedback += f"\nPronunciation Clarity: {clarity}%"
    return feedback


def generate_smart_report(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity):
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
    10. Pronunciation Clarity: {clarity}%
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
        
        clarity = evaluate_pronunciation_clarity(audio_file)
        logger.info("Pronunciation clarity evaluation complete")

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