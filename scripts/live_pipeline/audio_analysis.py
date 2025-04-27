import torch
import sounddevice as sd
import numpy as np
from transformers import (
    Wav2Vec2Tokenizer,
    Wav2Vec2FeatureExtractor,
    Wav2Vec2ForCTC,
)

SAMPLE_RATE = 16000

# Load Wav2Vec2 model components
tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
model.eval()

def record_audio(duration=10):
    print(f"[AUDIO] Recording for {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    return np.squeeze(audio).astype(np.float32) / 32768.0

def transcribe_audio(audio_data):
    inputs = feature_extractor(audio_data, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    return tokenizer.batch_decode(predicted_ids)[0].strip().lower()
