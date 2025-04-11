# JagCoaching - AI-Powered Presentation Coaching

JagCoaching is an AI-powered platform that provides real-time feedback on presentation skills, including eye contact, facial expressions, posture, and voice quality.

## Features

- Real-time video and audio analysis
- Feedback on eye contact, facial expressions, posture, and voice
- AI-generated personalized coaching tips
- Session history and progress tracking
- User authentication and profile management

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- MongoDB (local or Atlas)
- Google Gemini API key

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/jagcoaching.git
   cd jagcoaching
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   MONGODB_URL=your_mongodb_connection_string
   SECRET_KEY=your_secret_key_for_jwt
   GOOGLE_API_KEY=your_gemini_api_key
   ```

5. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd src/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Access the application at `http://localhost:5173`

## System Requirements

- **CPU**: Quad-core processor or better
- **RAM**: Minimum 8GB (16GB recommended)
- **GPU**: Not required but recommended for better performance
- **Disk Space**: At least 5GB free space
- **Camera**: Any standard webcam
- **Microphone**: Any standard microphone

## Dependencies

The application relies on several key libraries:

- **FastAPI**: Backend web framework
- **React**: Frontend framework
- **TensorFlow/PyTorch**: Machine learning frameworks
- **OpenCV**: Computer vision
- **DeepFace**: Facial analysis
- **Transformers**: NLP and audio processing
- **SoundDevice**: Audio recording and processing
- **MongoDB**: Database

## Troubleshooting

### Common Issues

1. **Dlib Installation**: If you encounter issues installing dlib, you may need to install CMake and a C++ compiler first.

2. **Audio Detection**: If audio is not being detected properly, check your microphone settings and ensure it has proper permissions.

3. **Camera Access**: If the camera doesn't initialize, ensure your browser has permission to access the camera.

4. **Model Downloads**: On first run, the application will download several ML models which may take some time depending on your internet connection.

## License

[MIT License](LICENSE)
