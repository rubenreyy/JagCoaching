import torch
import librosa
import numpy as np
from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration
from keybert import KeyBERT
from scipy.signal import find_peaks
from time import time
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()

# Must install torch torchaudio transformers librosa numpy scipy keybert google-genai python-dotenv

# TODO: Add error handling, logging, and unit tests

device = "cuda:0" if torch.cuda.is_available() else "cpu" # USE GPU IF AVAILABLE

def transcribe_speech(audio_path):
    """ Convert speech to text using Whisper """
    processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2", language="en")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2")
    
    audio, sr = librosa.load(audio_path, sr=16000)
    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").input_features
    
    with torch.no_grad():
        predicted_ids = model.generate(inputs)
    transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcript

def analyze_sentiment(text):
    """ Analyze sentiment of the speech """
    sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", device=0)
    return sentiment_pipeline(text)

def detect_filler_words(text):
    """ Count occurrences of filler words """
    fillers = ["uh", "um", "like", "you know", "so", "actually", "basically"]
    word_list = text.lower().split()
    filler_count = {word: word_list.count(word) for word in fillers if word in word_list}
    return filler_count

def analyze_emotion(audio_path):
    """ Analyze emotions in speech """
    emotion_pipeline = pipeline("audio-classification", model="superb/hubert-large-superb-er", device=0)
    return emotion_pipeline(audio_path)

def extract_keywords(text):
    """ Extract key topics using KeyBERT """
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
    return [kw[0] for kw in keywords]

def detect_pauses(audio_path):
    """ Detect significant pauses in speech """
    audio, sr = librosa.load(audio_path, sr=16000)
    energy = librosa.feature.rms(y=audio)[0]
    peaks, _ = find_peaks(-energy, distance=sr//2, height=-np.mean(energy))
    return len(peaks)

def analyze_speech_rate(transcript, audio_path):
    """ Calculate words per minute (WPM) """
    audio, sr = librosa.load(audio_path, sr=16000)
    duration = librosa.get_duration(y=audio, sr=sr)
    word_count = len(transcript.split())
    wpm = (word_count / duration) * 60
    return round(wpm, 2)

def grammar_correction(text):
    """ Perform grammar correction using a language model """
    grammar_pipeline = pipeline("text2text-generation", model="grammarly/coedit-large", device=0)
    corrected_text = grammar_pipeline(text, max_length=512)[0]['generated_text']
    return corrected_text

def analyze_monotone_speech(audio_path):
    """ Detect monotone speech patterns by analyzing pitch variance """
    audio, sr = librosa.load(audio_path, sr=16000)
    pitch, _ = librosa.piptrack(y=audio, sr=sr)
    pitch = pitch[pitch > 0]  # Remove zero values
    pitch_variance = np.var(pitch)
    return "Monotone" if pitch_variance < 500 else "Dynamic"

def evaluate_pronunciation_clarity(audio_path):
    """ Evaluate pronunciation clarity based on articulation features """
    clarity_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h", device=0)
    transcription = clarity_pipeline(audio_path)["text"]
    clarity_score = len([word for word in transcription.split() if word.isalpha()]) / len(transcription.split())
    return round(clarity_score * 100, 2)

def generate_feedback(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity):
    """ Generate structured feedback """
    feedback = "Speech Feedback Report:\n"
    feedback += f"\nTranscription: {transcript[:200]}..."  # Show first 200 chars
    feedback += f"\n\nSentiment: {sentiment[0]['label']} ({sentiment[0]['score']:.2f})"
    feedback += f"\nDetected Filler Words: {filler_words}"
    feedback += f"\nEmotions: {emotion[0]['label']} ({emotion[0]['score']:.2f})"
    feedback += f"\nKey Topics: {', '.join(keywords)}"
    feedback += f"\nNumber of Significant Pauses: {pauses}"
    feedback += f"\nSpeech Rate: {wpm} words per minute"
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
    7. Speech Rate: {wpm} words per minute
    8. Grammar Corrections: {corrected_text}
    9. Speech Tone: {monotone}
    10. Pronunciation Clarity: {clarity}%
    
    Provide actionable insights and suggestions for improvement.
    """
    google_gemini_api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
    client = genai.Client(api_key= google_gemini_api_key)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents= [prompt],
        config= types.GenerateContentConfig(
            system_instruction="You are an expert speech coach. Provide a detailed feedback report based on the following analysis",
            response_mime_type="application/json",
            stop_sequences=["\n\n"],)
        
    )
    print(response)
    return response.text

def main():
    # Example Usage 
    audio_file = "scripts\\tests\\Student_1.wav"  # Path to speech file
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

    # feedback_report = generate_feedback(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    # print(feedback_report)
    
    smart_report = generate_smart_report(transcript, sentiment, filler_words, emotion, keywords, pauses, wpm, corrected_text, monotone, clarity)
    print(smart_report)

if __name__ == "__main__":
    start_time = time()
    main()
    print(f"Execution time: {time() - start_time:.2f} seconds")