import speech_analysis
import json
import uuid
from datetime import datetime

# -- Speech Analysis Object --
# This class is a wrapper around the speech analysis functions in the speech_analysis.py file.

# -- Creating a class that will take in an audio file and return a structured feedback report --
class SpeechAnalysisObject:
    """_summary_: Speech Analysis that takes in an audio file and returns a structured feedback report
    """
    def __init__(self, audio_path, user_id=None):
        # Core Properties
        self.audio_path = audio_path
        self.user_id = user_id if user_id else str(uuid.uuid4())
        self.analysis_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        
        
        # Analysis Properties
        self.transcript = speech_analysis.transcribe_speech(audio_path)
        self.sentiment = speech_analysis.analyze_sentiment(self.transcript)
        self.filler_words = speech_analysis.detect_filler_words(self.transcript)
        self.emotion = speech_analysis.analyze_emotion(audio_path)
        self.keywords = speech_analysis.extract_keywords(self.transcript)
        self.pauses = speech_analysis.detect_pauses(audio_path)
        self.wpm = speech_analysis.analyze_speech_rate(self.transcript, audio_path)
        self.corrected_text = speech_analysis.grammar_correction(self.transcript)
        self.monotone = speech_analysis.analyze_monotone_speech(audio_path)
        self.clarity = speech_analysis.evaluate_pronunciation_clarity(audio_path)
    
    def generate_feedback(self):
        """ Generate structured feedback(truncated feedback) """
        feedback = speech_analysis.generate_feedback(self.transcript, self.sentiment, self.filler_words, self.emotion, self.keywords, self.pauses, self.wpm, self.corrected_text, self.monotone, self.clarity) 
        return feedback
    
    def generate_smart_report(self):
        """_summary_: Generate a smart feedback report using Google GenAI

        Returns:
            _type_: JSON response from Google GenAI API
        """
        smart_report = speech_analysis.generate_smart_report(self.transcript, self.sentiment, self.filler_words, self.emotion, self.keywords, self.pauses, self.wpm, self.corrected_text, self.monotone, self.clarity)
        return smart_report
    
    def to_dict(self):
        """ Convert instance properties to a dictionary """
        return vars(self)

    def to_json(self):
        """ Convert instance properties to a JSON string """
        return json.dumps(self.to_dict(), indent=4)

    def save_feedback_to_file(self, file_path):
        """ Save feedback to a JSON file """
        with open(file_path, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)


# -- Example Usage --
def main():
    # Example Usage
    audio_file = "scripts\\tests\\Student_2.wav"  # Path to speech file
    analysis = SpeechAnalysisObject(audio_file)
    feedback_report = analysis.generate_feedback()
    print(feedback_report)
    print(analysis.to_dict())
    print(analysis.to_json())
    # analysis.save_feedback_to_file("feedback.json")


if __name__ == "__main__":
    main()