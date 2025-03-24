import pytest
from SpeechAnalysisObject import SpeechAnalysisObject

@pytest.fixture
def sample_speech_analysis():
    # Create an instance of SpeechAnalysisObject
    return SpeechAnalysisObject("Student_1.wav")

def test_initialization(sample_speech_analysis):
    # Check if the object is initialized correctly
    assert sample_speech_analysis.file_path == "Student_1.wav"

def test_load_audio(sample_speech_analysis):
    # Check if the audio file is loaded correctly
    sample_speech_analysis.load_audio()
    assert sample_speech_analysis.audio_data is not None

def test_transcribe_audio(sample_speech_analysis):
    # 
    sample_speech_analysis.load_audio()
    transcription = sample_speech_analysis.transcribe_audio()
    assert isinstance(transcription, str)
    assert len(transcription) > 0

def test_analyze_sentiment(sample_speech_analysis):
    sample_speech_analysis.load_audio()
    transcription = sample_speech_analysis.transcribe_audio()
    sentiment = sample_speech_analysis.analyze_sentiment(transcription)
    assert sentiment in ["positive", "neutral", "negative"]

def test_extract_keywords(sample_speech_analysis):
    sample_speech_analysis.load_audio()
    transcription = sample_speech_analysis.transcribe_audio()
    keywords = sample_speech_analysis.extract_keywords(transcription)
    assert isinstance(keywords, list)
    assert len(keywords) > 0

if __name__ == "__main__":
    pytest.main()