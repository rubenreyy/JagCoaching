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
import json
import logging
import whisper

# Set cache directories to avoid root overflow
os.environ["XDG_CACHE_HOME"] = "/mnt/disk-6/.cache"
os.environ["TRANSFORMERS_CACHE"] = "/mnt/disk-6/.hf_cache"
load_dotenv("./.env.development")

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Configure logging
logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=40)
def load_librosa(audio_path):
    try:
        audio, sr = librosa.load(audio_path, sr=16000, duration=300)
        return audio, sr
    except Exception as e:
        logger.error(f"Error loading audio file {audio_path}: {e}")
        return None, None

def transcribe_speech(audio_path):
    try:
        logger.info(f"Starting transcription for {audio_path}")
        model = whisper.load_model("medium")
        logger.info("Whisper model loaded successfully")
        result = model.transcribe(audio_path, language="en", task="transcribe", verbose=False)
        logger.info("Transcription completed successfully")
        return result["text"]
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise

@functools.lru_cache(maxsize=1)
def get_sentiment_model():
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return tokenizer, model

def analyze_sentiment(text):
    tokenizer, model = get_sentiment_model()
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        label_idx = scores.argmax().item()
        score = scores[0][label_idx].item()

    label_map = ["Negative", "Neutral", "Positive"]
    label = label_map[label_idx]

    return {
        "label": label,
        "score": score,
        "suggestion": (
            "Your tone is well-balanced and professional." if label == "Neutral"
            else "Consider maintaining a more neutral tone." if label == "Negative"
            else "Your positive tone helps engage the audience."
        )
    }

def detect_filler_words(text):
    fillers = ["uh", "um", "like", "you know", "so", "actually", "basically"]
    word_list = text.lower().split()
    filler_count = {word: word_list.count(word) for word in fillers if word in word_list}
    total_fillers = sum(filler_count.values())
    return {
        "counts": filler_count,
        "total": total_fillers,
        "suggestion": (
            "Great job minimizing filler words!" if total_fillers <= 2
            else "Try to reduce filler words by pausing briefly instead."
        )
    }

def analyze_emotion(audio_path):
    emotion_pipeline = pipeline("audio-classification", model="superb/hubert-large-superb-er", device=device, batch_size=4)
    return emotion_pipeline(audio_path)

def extract_keywords(text):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
    return [kw[0] for kw in keywords]

def detect_pauses(audio_path):
    audio, sr = load_librosa(audio_path)
    energy = librosa.feature.rms(y=audio)[0]
    peaks, _ = find_peaks(-energy, distance=sr//2, height=-np.mean(energy))
    return len(peaks)

def analyze_speech_rate(transcript, audio_path):
    audio, sr = load_librosa(audio_path)
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

def grammar_correction(text):
    grammar_pipeline = pipeline("text2text-generation", model="grammarly/coedit-large", device=device)
    return grammar_pipeline(text, max_length=512)[0]['generated_text']

def analyze_monotone_speech(audio_path):
    audio, sr = load_librosa(audio_path)
    pitch, _ = librosa.piptrack(y=audio, sr=sr)
    pitch = pitch[pitch > 0]
    pitch_variance = np.var(pitch)
    return "Monotone" if pitch_variance < 500 else "Dynamic"

def evaluate_pronunciation_clarity(audio_path):
    clarity_pipeline = pipeline(
        "automatic-speech-recognition",
        model="facebook/wav2vec2-base-960h",
        device=device,
        batch_size=4,
        torch_dtype=torch.float32,
    )
    transcription = clarity_pipeline(audio_path)["text"]
    clarity_score = len([word for word in transcription.split() if word.isalpha()]) / len(transcription.split())
    return round(clarity_score * 100, 2)

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
        client = genai.Client(api_key=os.environ.get("GOOGLE_GEMINI_API_KEY"))
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
        return "An error occurred during smart feedback generation."

def main():
    audio_file = "scripts/tests/Student_1.wav"
    transcript = transcribe_speech(audio_file)
    sentiment = analyze_sentiment(transcript)
    filler_words = detect_filler_words(transcript)
    emotion = analyze_emotion(audio_file)
    keywords = extract_keywords(transcript)
    pauses = detect_pauses(audio_file)
    wpm = analyze_speech_rate(transcript, audio_file)
    corrected_text = grammar_correction(transcript)
    monotone = analyze_monotone_speech(audio_file)
    clarity = evaluate_pronunciation_clarity(audio_file)

    feedback_report = generate_feedback(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    print(feedback_report)

    smart_report = generate_smart_report(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    print(smart_report)

if __name__ == "__main__":
    start_time = time()
    main()
    print(f"Execution time: {time() - start_time:.2f} seconds")