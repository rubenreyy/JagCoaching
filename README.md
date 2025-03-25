# JagCoaching
AI-powered presentation analysis tool by Ruben Reyes, Chris Nastasi, Angelo Badiola, Mel Nunez, Brandon Martinez, and Andrew Gonzalez.

## Key Changes Made
1. **Authentication System**
   - Implemented JWT token-based auth
   - Added user sessions management
   - Secured API endpoints

2. **Video Processing**
   - Added robust error handling
   - Improved file upload process
   - Added audio extraction pipeline
   - Enhanced feedback generation

3. **Database Integration**
   - MongoDB Cloud integration
   - User data persistence
   - Video analysis storage

## Setup Instructions

### Prerequisites
- Python 3.12.9
- Node.js v18+
- MongoDB Atlas account
- Hugging Face API key
- Google Gemini API key
- FFmpeg (for audio processing)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/JagCoaching.git
cd JagCoaching
```

2. Set up Python environment (choose one method):

   **Method 1 - Using venv and pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Method 2 - Using pipenv:**
   ```bash
   pip install pipenv
   pipenv install
   pipenv shell
   ```

3. Set up environment variables:
   - Copy `.env.development.example` to `.env.development`
   - Add your credentials:
   ```env
   HUGGINGFACE_API_KEY=your_key
   GOOGLE_GEMINI_API_KEY=your_key
   MONGO_DB_URI=your_mongodb_uri
   SECRET_KEY=your_secret_key
   ```

4. Start the backend server:
```bash
cd src/backend
uvicorn main:app --reload
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd src/frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

### Accessing the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

### Troubleshooting Common Issues

1. **Package Installation Issues:**
   - Try upgrading pip: `python -m pip install --upgrade pip`
   - If using pipenv: `pipenv clean && pipenv install`
   - If using requirements.txt: `pip install -r requirements.txt --upgrade`

2. **FFmpeg Missing:**
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from official FFmpeg website

3. **Torch Installation Issues:**
   - If GPU support needed: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
   - For CPU only: `pip install torch torchvision torchaudio`

4. **MongoDB Connection Issues:**
   - Verify MongoDB Atlas whitelist includes your IP
   - Check connection string format
   - Ensure network connectivity

### Using the Application

1. **Create an Account**
   - Click "Sign Up" on the homepage
   - Enter email and password
   - Verify your account

2. **Login**
   - Use your email and password
   - Keep note of your authentication token

3. **Upload a Video**
   - Must be logged in
   - Supported formats: .mp4, .mov, .avi, .webm
   - Wait for processing (can take several minutes)

4. **View Feedback**
   - Analysis includes:
     - Transcription
     - Sentiment analysis
     - Filler word detection
     - Speech clarity metrics
     - Speaking pace (WPM)

### Troubleshooting

1. **Authentication Issues**
   - Clear browser cache
   - Check token expiration
   - Verify credentials in .env file

2. **Upload Problems**
   - Ensure file size < 100MB
   - Check supported formats
   - Verify MongoDB connection

3. **Processing Errors**
   - Check API keys
   - Verify Python dependencies
   - Check server logs

## Contributing
Please create a new branch for features:
```bash
git checkout -b feature-name
```

## Project Structure

## Frontend Features
- Complete authentication flow (Login/Signup)
- User account management
- Responsive navigation
- Mobile-friendly design
- Consistent UI styling across all pages
- IBM Plex Mono font integration
- Interactive components with hover states
- Form validation
- Protected routes based on authentication

## Frontend Technologies
- React 18 (UI Library)
- Vite (Build Tool)
- Tailwind CSS (Styling)
- Lucide React (Icons)
- IBM Plex Mono (Font Family)

## Frontend Development

1. Make sure you're in the frontend directory:
```bash
cd src/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. View the application at: `http://localhost:5173`

## Frontend Troubleshooting

If you encounter issues with the frontend:

1. Clear npm cache and reinstall dependencies:
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

2. Make sure you're running the correct Node.js version:
```bash
node --version  # Should be v18.0.0 or higher
```

3. If styles aren't updating, try clearing your browser cache

# Technologies Used: 

# Front End
- React 18
- Vite
- Tailwind CSS
- IBM Plex Mono font family

## Frontend Setup
1. Navigate to frontend directory:
```bash
cd src/frontend
```
2. Install dependencies:
```bash
npm install
```
3. Start the development server:
```bash
npm run dev
```
4. Open browser and visit: `http://localhost:5173`

## Required Dependencies
- Node.js (v18.0.0 or higher)
- npm (comes with Node.js)

## Frontend Structure

src/frontend/
├── public/ # Static assets
├── src/ # Source code
│ ├── assets/ # Images, icons, etc.
│ ├── components/ # Reusable components
│ ├── App.jsx # Main App component
│ └── main.jsx # Entry point

# Back End


# AI
