import os
import functools
from time import time
import numpy as np
import torch
import librosa
from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration, WhisperConfig 
from keybert import KeyBERT
from scipy.signal import find_peaks
import google.generativeai as genai
from google.genai import types
from dotenv import load_dotenv
import json
import logging
# Load environment variables from .env file in scripts folder only
load_dotenv("./.env.development")

""" Speech Analysis Pipeline """

# Avoids CUDA out of memory error
blocking = os.environ.get("CUDA_LAUNCH_BLOCKING")
print(blocking)
# Must install torch torchaudio transformers librosa numpy scipy keybert python-dotenv

# TODO: Add error handling, and logging, make it more efficient and scalable

device = "cuda:0" if torch.cuda.is_available() else "cpu"  # USE GPU IF AVAILABLE

# FIXME: Load audio librosa only once

# Configure logging
logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=40)
def load_librosa(audio_path):
    """ Load audio file using librosa """
    try:
        audio, sr = librosa.load(audio_path, sr=16000, duration=300)
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {e}")
        return None, None
    return audio, sr


def transcribe_speech(audio_path):
    """ Convert speech to text using Whisper """
    try:
        logger.info(f"Starting transcription for {audio_path}")
        model = "openai/whisper-large-v2"
        logger.info("Loading Whisper model and processor...")
        
        processor = WhisperProcessor.from_pretrained(model)
        model = WhisperForConditionalGeneration.from_pretrained(model)
        model.config = WhisperConfig(torchscript=True, return_timestamps=True, language="en",
                                 task="transcribe")
        
        logger.info("Loading audio file...")
        audio, sr = load_librosa(audio_path)
        if audio is None:
            raise ValueError("Failed to load audio file")
            
        logger.info("Processing audio through model...")
        inputs = processor(audio, sampling_rate=sr, return_tensors="pt",
                       truncation=False).input_features
        inputs = inputs.to(device, dtype=torch.float32, non_blocking=True)
        attention_mask = torch.ones(1, 2000).to(device)
        model = model.to(device)

        logger.info("Generating transcription...")
        with torch.no_grad():
            predicted_ids = model.generate(
                input_features=inputs, 
                attention_mask=attention_mask,
                num_beams=1,
                return_timestamps=True,
                early_stopping=False,
                language="en",
                task="transcribe"
            )
        
        transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        logger.info("Transcription completed successfully")
        return transcript

    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise

# FIXME: this pipeline is cleaner and easier than the one above ^^^


def test_pipeline(audio_path):
    """_summary_"""
    # Implement this eventually
    # processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    # model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h", torch_dtype=torch.float16).to(device)

    transcribe = pipeline(task="automatic-speech-recognition",
                          model="openai/whisper-base", use_fast=True)
    audio, sr = load_librosa(audio_path)
    transcript = transcribe(audio, return_timestamps=True)

    return transcript


def analyze_sentiment(text):
    """ Analyze sentiment with human-readable labels """
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="cardiffnlp/twitter-roberta-base-sentiment", 
        device=device
    )
    result = sentiment_pipeline(text)[0]
    
    # Map technical labels to human-readable ones
    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }
    
    return {
        "label": label_map.get(result["label"], result["label"]),
        "score": result["score"],
        "suggestion": (
            "Your tone is well-balanced and professional." if result["label"] == "LABEL_1"
            else "Consider maintaining a more neutral tone." if result["label"] == "LABEL_0"
            else "Your positive tone helps engage the audience."
        )
    }


def detect_filler_words(text):
    """ Count occurrences of filler words and provide suggestions """
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
    """ Analyze emotions in speech """
    emotion_pipeline = pipeline(
        "audio-classification", model="superb/hubert-large-superb-er", device=device, batch_size=4)
    return emotion_pipeline(audio_path)


def extract_keywords(text):
    """ Extract key topics using KeyBERT """
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
    return [kw[0] for kw in keywords]


def detect_pauses(audio_path):
    """ Detect significant pauses in speech """
    audio, sr = load_librosa(audio_path)
    energy = librosa.feature.rms(y=audio)[0]
    peaks, _ = find_peaks(-energy, distance=sr//2, height=-np.mean(energy))
    return len(peaks)


def analyze_speech_rate(transcript, audio_path):
    """ Calculate words per minute (WPM) and provide context """
    audio, sr = load_librosa(audio_path)
    duration = librosa.get_duration(y=audio, sr=sr)
    word_count = len(transcript.split())
    wpm = (word_count / duration) * 60
    
    # Add context about speech rate
    rate_context = {
        "wpm": round(wpm, 2),
        "assessment": "optimal" if 120 <= wpm <= 150 else "too slow" if wpm < 120 else "too fast",
        "suggestion": (
            "Your speaking pace is ideal for clear communication." if 120 <= wpm <= 150
            else "Consider speaking a bit faster to maintain engagement." if wpm < 120
            else "Try slowing down slightly for better clarity."
        )
    }
    return rate_context


def grammar_correction(text):
    """ Perform grammar correction using a language model """
    grammar_pipeline = pipeline(
        "text2text-generation", model="grammarly/coedit-large", device=device)
    corrected_text = grammar_pipeline(text, max_length=512)[
        0]['generated_text']
    return corrected_text


def analyze_monotone_speech(audio_path):
    """ Detect monotone speech patterns by analyzing pitch variance """
    audio, sr = load_librosa(audio_path)
    pitch, _ = librosa.piptrack(y=audio, sr=sr)
    pitch = pitch[pitch > 0]  # Remove zero values
    pitch_variance = np.var(pitch)
    return "Monotone" if pitch_variance < 500 else "Dynamic"


def evaluate_pronunciation_clarity(audio_path):
    """ Evaluate pronunciation clarity based on articulation features """
    # Use a lighter model with faster inference and load in FP16 for better GPU utilization
    clarity_pipeline = pipeline(
        "automatic-speech-recognition",
        model="facebook/wav2vec2-base-960h",  # Smaller model, faster inference
        device=device,
        batch_size=4,  # Process more audio in parallel if memory allows
        torch_dtype=torch.float32,  # Use half precision for faster processing and less memory

    )

    transcription = clarity_pipeline(audio_path)["text"]
    clarity_score = len([word for word in transcription.split(
    ) if word.isalpha()]) / len(transcription.split())
    return round(clarity_score * 100, 2)


def generate_feedback(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity):
    """ Generate structured feedback """
    feedback = "Speech Feedback Report:\n"
    # Show first 200 chars
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
    """ Generate a smart feedback report using Google GenAI """
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
    google_gemini_api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
    client = genai.Client(api_key=google_gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[prompt],
        config=types.GenerateContentConfig(
            system_instruction="You are an expert speech coach. Provide a detailed feedback report based on the following analysis",
            response_mime_type="application/json",
            stop_sequences=["\n\n"],)

    )
    print(response)
    return response.text


def main():

    # Example Usage
    audio_file = "scripts/tests/Student_1.wav"  # Path to speech file
    # transcript = transcribe_speech(audio_file)
    # print(transcript)
    transcript = test_pipeline(audio_file)
    print(transcript)
    # summary = testing_summarization(transcript)
    # print(summary)
    # sentiment = analyze_sentiment(transcript)
    # filler_words = detect_filler_words(transcript)
    # emotion = analyze_emotion(audio_file)
    # keywords = extract_keywords(transcript)
    # pauses = detect_pauses(audio_file)
    # wpm = analyze_speech_rate(transcript, audio_file)
    # corrected_text = grammar_correction(transcript)
    # monotone = analyze_monotone_speech(audio_file)
    # clarity = evaluate_pronunciation_clarity(audio_file)
    # print(clarity)

    # feedback_report = generate_feedback(
    #     transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    # feedback_data = {
    #     "transcription": transcript[:200] + "...",
    #     "sentiment": {
    #         "label": sentiment['label'],
    #         "score": round(sentiment['score'], 2)
    #     },
    #     "filler_words": filler_words,
    #     "emotion": {
    #         "label": emotion[0]['label'],
    #         "score": round(emotion[0]['score'], 2)
    #     },
    #     "key_topics": keywords,
    #     "significant_pauses": pauses,
    #     "speech_rate_wpm": wpm['wpm'],
    #     "grammar_corrections": corrected_text,
    #     "speech_tone": monotone,
    #     "pronunciation_clarity_percentage": clarity
    # }
    
    # with open("scripts/tests/feedback_report.json", "w") as f:
    #     json.dump(feedback_data, f, indent=4)
    # print(feedback_report)
    

    # smart_report = generate_smart_report(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    # print(smart_report)



if __name__ == "__main__":
    start_time = time()
    main()
    print(f"Execution time: {time() - start_time:.2f} seconds")
