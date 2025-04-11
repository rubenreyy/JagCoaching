import torch
import sounddevice as sd
import numpy as np
import logging
from transformers import (
    Wav2Vec2Processor,
    Wav2Vec2ForCTC,
)

logger = logging.getLogger(__name__)
SAMPLE_RATE = 16000

# Load Wav2Vec2 model components with better error handling
processor = None
model = None

try:
    logger.info("Loading Wav2Vec2 model components...")
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
    model.eval()
    logger.info("Wav2Vec2 model components loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Wav2Vec2 model: {e}")
    # Don't raise here, we'll handle missing models gracefully

def record_audio(duration=5):
    """Record audio for the specified duration"""
    try:
        logger.info(f"Recording audio for {duration} seconds")
        # Increase volume sensitivity
        audio_data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.float32)
        sd.wait()
        
        # Normalize audio to increase volume
        audio = audio_data.flatten()
        max_amplitude = np.max(np.abs(audio))
        
        if max_amplitude > 0:
            # Apply much higher gain to make quiet speech more detectable
            # Increase from 1.5 to 5.0 for better sensitivity
            audio = audio * 5.0
            # Clip to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)
            
        logger.info(f"Recorded audio with max amplitude: {max_amplitude}")
        return audio
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        # Return empty audio array to avoid crashes
        return np.zeros(int(duration * SAMPLE_RATE), dtype=np.float32)

def transcribe_audio(audio_data):
    """
    Transcribe audio data to text.
    
    Args:
        audio_data: Audio data as numpy array or base64 encoded string
        
    Returns:
        str: Transcription text or status message
    """
    try:
        logger.info(f"Transcribing audio data of type {type(audio_data)}")
        
        # Handle base64 encoded audio
        if isinstance(audio_data, str):
            try:
                # Check if it's a base64 string
                if audio_data.startswith('data:audio'):
                    import base64
                    import re
                    
                    # Extract the base64 part
                    base64_data = re.sub('^data:audio/.+;base64,', '', audio_data)
                    audio_bytes = base64.b64decode(base64_data)
                    
                    # Convert to numpy array
                    import io
                    import wave
                    
                    with io.BytesIO(audio_bytes) as wav_io:
                        with wave.open(wav_io, 'rb') as wav_file:
                            frames = wav_file.getnframes()
                            audio_data = np.frombuffer(wav_file.readframes(frames), dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Apply gain to the converted audio data
                    audio_data = audio_data * 5.0
                    audio_data = np.clip(audio_data, -1.0, 1.0)
                    
                    logger.info(f"Successfully converted base64 audio to numpy array, shape: {audio_data.shape}")
                else:
                    logger.warning("Audio data is a string but not in expected base64 format")
                    return "Could not process audio format"
            except Exception as e:
                logger.error(f"Error processing base64 audio: {e}")
                return "Error processing audio"
        
        # Check if we have valid audio data
        if not isinstance(audio_data, np.ndarray):
            logger.warning(f"Invalid audio data type: {type(audio_data)}")
            return "No speech detected"
        
        # Check audio volume
        max_amplitude = np.max(np.abs(audio_data))
        logger.info(f"Audio max amplitude: {max_amplitude}")
        
        # Calculate non-zero ratio
        non_zero_ratio = np.count_nonzero(audio_data) / audio_data.size
        logger.info(f"Non-zero audio ratio: {non_zero_ratio:.4f}")
        
        # Calculate standard deviation to detect consistent speech vs random noise
        std_dev = np.std(audio_data)
        logger.info(f"Audio standard deviation: {std_dev:.6f}")
        
        # Calculate energy distribution across the sample
        # Split audio into segments and check if energy is distributed evenly (speech)
        # or concentrated in short bursts (random noises)
        segments = np.array_split(audio_data, 20)  # Split into 20 segments for finer analysis
        segment_energies = [np.sum(np.abs(segment)) for segment in segments]
        energy_std = np.std(segment_energies)
        energy_mean = np.mean(segment_energies)
        energy_cv = energy_std / energy_mean if energy_mean > 0 else 0  # Coefficient of variation
        logger.info(f"Energy distribution CV: {energy_cv:.4f}")
        
        # Calculate zero-crossing rate (higher for speech)
        zero_crossings = np.sum(np.abs(np.diff(np.signbit(audio_data)))) / len(audio_data)
        logger.info(f"Zero crossing rate: {zero_crossings:.4f}")
        
        # Calculate spectral centroid (measure of "brightness" of sound)
        # Higher for speech with consonants, lower for ambient noise
        if len(audio_data) > 0:
            # Simple spectral analysis
            from scipy import signal
            frequencies, power_spectrum = signal.welch(audio_data, fs=SAMPLE_RATE, nperseg=1024)
            if np.sum(power_spectrum) > 0:
                spectral_centroid = np.sum(frequencies * power_spectrum) / np.sum(power_spectrum)
                logger.info(f"Spectral centroid: {spectral_centroid:.2f} Hz")
            else:
                spectral_centroid = 0
                logger.info("No significant spectral content")
        else:
            spectral_centroid = 0
        
        # MUCH more aggressive speech detection
        # Combination of factors to detect actual speech vs background noise
        
        # 1. Check for actual speech patterns using multiple metrics
        is_speech = False
        
        # Speech typically has:
        # - Higher amplitude variations (std_dev > 0.003)
        # - More consistent energy across segments (energy_cv < 0.8)
        # - Higher zero-crossing rate (> 0.03 for speech)
        # - Spectral centroid in speech range (300-3000 Hz)
        
        if (std_dev > 0.003 and 
            energy_cv < 0.8 and 
            zero_crossings > 0.03 and 
            300 < spectral_centroid < 3000):
            is_speech = True
            logger.info("Speech pattern detected based on audio characteristics")
        
        # 2. Check for minimum amplitude threshold (much higher than before)
        if max_amplitude < 0.01:
            logger.info("Audio level too low for clear speech")
            return "No speech detected - please speak up"
        
        # 3. If we don't detect speech patterns, it's likely background noise
        if not is_speech:
            logger.info("No speech pattern detected - likely background noise")
            return "No speech detected - please speak up"
        
        # Now assess the quality of detected speech
        if max_amplitude < 0.02:
            logger.info("Audio detected but quiet")
            return "Speech detected, but volume is low - speak louder"
        elif max_amplitude < 0.05:
            logger.info("Audio level acceptable")
            return "Good volume level - speech is clear"
        elif max_amplitude < 0.1:
            logger.info("Audio level good")
            return "Excellent voice projection - very clear speech"
        else:
            logger.info("Audio level possibly too loud")
            return "Volume may be too loud - consider speaking a bit softer"
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return "Error processing audio"
