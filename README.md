# JagCoaching
AI-powered presentation analysis tool by Ruben Reyes, Chris Nastasi, Angelo Badiola, Mel Nunez, Brandon Martinez, and Andrew Gonzalez.

## Key Changes Made
1. **Authentication System**
   - Implemented JWT token-based auth using PyJWT
   - Added user sessions management
   - Secured API endpoints
   - Bcrypt password hashing

2. **Video Processing**
   - Added robust error handling
   - Improved file upload process
   - Added audio extraction pipeline
   - Enhanced feedback generation using Gemini AI

3. **Database Integration**
   - MongoDB Cloud integration
   - User data persistence
   - Video analysis storage
   - Secure connection handling

## New Features Added

### Real-Time Analysis
- Live video streaming via WebSocket
- Real-time audio processing
- Instant feedback generation
- Performance monitoring
- Network status tracking

### Error Handling & Monitoring
- Comprehensive error boundaries
- Performance metrics tracking
- Network condition monitoring
- Automatic error recovery
- Session persistence

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
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
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

### WebSocket Configuration

1. Enable WebSocket in your environment:
```env
ENABLE_WEBSOCKET=true
WEBSOCKET_PORT=8001
```

2. Configure CORS for WebSocket:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Performance Monitoring

1. Enable monitoring:
```env
ENABLE_MONITORING=true
PROMETHEUS_PORT=9090
```

2. Monitor metrics at:
- Frontend Performance: http://localhost:5173/metrics
- Backend Metrics: http://localhost:9090/metrics

### Network Requirements
- Minimum upload speed: 1 Mbps
- Minimum download speed: 2 Mbps
- Stable connection for WebSocket
- Low latency for real-time analysis

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

#### WebSocket Connection Issues
1. Check WebSocket server status:
```bash
curl -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:8001" \
  -H "Origin: http://localhost:5173" \
  "ws://localhost:8001"
```

2. Verify network conditions:
```bash
ping localhost -c 4
```

#### Performance Issues
1. Monitor system resources:
```bash
top  # or htop if installed
```

2. Check application metrics:
- Open browser dev tools
- Navigate to Performance tab
- Record page load and interactions

#### Camera/Microphone Access
1. Check browser permissions
2. Verify device connections
3. Test devices in browser settings

### Error Recovery Procedures

1. Connection Loss
- Automatic reconnection attempts
- Session state preservation
- Data recovery when possible

2. Performance Degradation
- Automatic quality adjustment
- Resource usage optimization
- Background task throttling

3. Device Failures
- Fallback to alternative devices
- Graceful degradation
- User notification system

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

### Important Package Dependencies
Make sure these key packages are properly installed:
```bash
pip install "PyJWT>=2.10.1"  # For JWT authentication
pip install "passlib[bcrypt]>=1.7.4"  # For password hashing
pip install "python-multipart>=0.0.9"  # For file uploads
pip install "pydantic-settings>=2.8.1"  # For settings management
```

### Authentication System
The system uses:
- PyJWT for token generation and validation
- Bcrypt for password hashing
- OAuth2 password flow with Bearer tokens
- Secure session management

## Testing Different Network Conditions

### Chrome DevTools
1. Open DevTools (F12)
2. Go to Network tab
3. Use network throttling presets:
   - Fast 3G
   - Slow 3G
   - Offline

### Real Network Testing
1. Test on different networks:
   - WiFi
   - Mobile data
   - Public networks

2. Monitor connection quality:
   - Check Network Monitor component
   - Observe WebSocket stability
   - Monitor error rates

## Performance Optimization Tips

1. Video Stream
   - Reduce resolution if needed
   - Adjust frame rate
   - Use compression

2. Audio Stream
   - Adjust chunk size
   - Modify bitrate
   - Balance quality vs performance

3. Real-time Analysis
   - Enable/disable features based on performance
   - Implement progressive enhancement
   - Use lazy loading where possible
