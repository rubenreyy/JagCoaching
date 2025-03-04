# JagCoaching Backend

## Overview
The backend for the JagCoaching platform is built using **FastAPI** and is responsible for processing video uploads, extracting audio, transcribing speech, and evaluating presentations using an **LLM (Large Language Model)**.

## Features
- **Video Upload**: Supports video file uploads.
- **Audio Processing**: Extracts audio from video files.
- **Speech-to-Text**: Uses **OpenAI Whisper** to transcribe speech.
- **AI Evaluation**: Uses an **open-source LLM (Mistral-7B)** to analyze speech quality and provide feedback.

## Project Structure
```
src/backend/
│── main.py          # FastAPI application
│── config.py        # Configuration settings
│── utils.py         # Helper functions for processing
│── models.py        # API request/response models
│── requirements.txt # Dependencies
│── uploads/         # Directory for uploaded files
```

## Installation
### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Running the Server
```sh
uvicorn main:app --reload
```

## API Endpoints
### 1. Upload Video
**Endpoint:** `POST /upload/`
- **Description:** Uploads a video file.
- **Request:** `multipart/form-data`
- **Response:**
```json
{
  "filename": "example.mp4",
  "status": "uploaded"
}
```

### 2. Process Audio
**Endpoint:** `POST /process-audio/`
- **Description:** Extracts audio and transcribes speech.
- **Request:**
```json
{
  "file_name": "example.mp4"
}
```
- **Response:**
```json
{
  "transcript": "Hello everyone, welcome to my talk...",
  "audio_path": "uploads/example.wav"
}
```

### 3. Evaluate Speech
**Endpoint:** `POST /evaluate-speech/`
- **Description:** Uses LLM to analyze the speech transcript.
- **Request:**
```json
{
  "transcript": "Hello everyone, welcome to my talk..."
}
```
- **Response:**
```json
{
  "feedback": "Your speech was clear but could use more variation in tone."
}
```

## Deployment
To deploy using **Docker**, create a `Dockerfile` and use:
```sh
docker build -t jagcoaching-backend .
docker run -p 8000:8000 jagcoaching-backend
```

## Future Enhancements
- **Database Integration** for storing transcripts and feedback.
- **Real-time Speech Analysis** using WebSockets.
- **Improved AI Models** for deeper presentation insights.

## Contributors
- Backend Developer: **[Your Name]**
- AI Research: **[Your Team Member]**
- Full Stack Support: **[Other Contributors]**

## License
MIT License
