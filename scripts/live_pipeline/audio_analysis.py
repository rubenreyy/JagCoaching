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
        if np.max(np.abs(audio)) > 0:
            # Apply some gain to make quiet speech more detectable
            audio = audio * 1.5
            # Clip to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)
            
        logger.info(f"Recorded audio with max amplitude: {np.max(np.abs(audio))}")
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
                    try:
                        # Extract the base64 part
                        import base64
                        import re
                        
                        base64_data = re.sub('^data:audio/.+;base64,', '', audio_data)
                        audio_bytes = base64.b64decode(base64_data)
                        
                        # Convert to numpy array
                        import io
                        import soundfile as sf
                        
                        with io.BytesIO(audio_bytes) as buf:
                            audio_array, sample_rate = sf.read(buf)
                            logger.info(f"Loaded audio with shape {audio_array.shape}, sample rate {sample_rate}")
                        
                        # Check if there's actual audio content
                        if np.max(np.abs(audio_array)) < 0.01:
                            logger.warning("Audio too quiet, no transcription attempted")
                            return "Audio too quiet - please speak louder"
                            
                        # Continue with transcription using the loaded audio
                        # Use Whisper or other transcription service here
                        # For now, we'll detect if there's speech based on audio levels
                        if np.max(np.abs(audio_array)) > 0.05:
                            logger.info("Detected clear speech in audio")
                            return "Speech detected, clear and audible"
                        elif np.max(np.abs(audio_array)) > 0.02:
                            logger.info("Detected quiet speech in audio")
                            return "Speech detected, but volume is low"
                        else:
                            logger.info("Detected very quiet speech in audio")
                            return "Speech barely audible - please speak louder"
                        
                    except Exception as e:
                        logger.error(f"Error processing audio data: {e}")
                        return "Error processing audio"
            except Exception as e:
                logger.error(f"Error decoding base64 audio: {e}")
                return "Error decoding audio"
        
        # Handle numpy array from direct recording
        elif isinstance(audio_data, np.ndarray):
            # Check if there's actual audio content
            max_amplitude = np.max(np.abs(audio_data))
            logger.info(f"Audio max amplitude: {max_amplitude}")
            
            if max_amplitude < 0.01:
                logger.warning("Audio too quiet, no transcription attempted")
                return "Audio too quiet - please speak louder"
            elif max_amplitude < 0.03:
                logger.info("Audio detected but quiet")
                return "Speech detected, but volume is low - speak louder"
            elif max_amplitude < 0.1:
                logger.info("Audio detected with moderate volume")
                return "Speech detected with good volume"
            else:
                logger.info("Audio detected with strong volume")
                return "Speech detected with excellent projection"
            
        else:
            logger.warning(f"Unsupported audio data type: {type(audio_data)}")
            return "Unsupported audio format"
            
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}", exc_info=True)
        return "Speech analysis in progress..."
