# Live Pipeline Scripts

This directory contains scripts for real-time analysis and feedback during live coaching sessions. Each script serves a specific role in processing video and audio data, analyzing user performance, and generating actionable feedback.

## Scripts Overview

- **live_analysis_pipeline.py**  
    Orchestrates the live analysis process. It runs face and audio analysis on incoming data, aggregates results, and formats feedback for the backend. It serves as the main entry point for running a single analysis or a continuous feedback loop.

- **face_analysis.py**  
    Contains functions for analyzing facial expressions, eye contact, and posture from video frames. Used by the main pipeline to extract visual metrics.

- **audio_analysis.py**  
    Handles audio recording and transcription. Provides utilities to record short audio clips and transcribe them for further analysis.

- **live_gemini.py**  
    Integrates with the Gemini feedback system to generate detailed, AI-powered feedback based on the results of face and audio analysis.

---

Each script is designed to be modular and reusable, supporting both synchronous and asynchronous workflows for live coaching scenarios.