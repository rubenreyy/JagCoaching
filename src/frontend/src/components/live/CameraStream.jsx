import { useEffect, useRef, useState, useCallback } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import PropTypes from 'prop-types';

const CAPTURE_INTERVAL = 1000; // Capture frame every 1 second
const AUDIO_CHUNK_SIZE = 3000; // Send audio every 3 seconds

const CameraStream = ({ onError, isRecording }) => {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const captureIntervalRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const {
    sendVideoFrame,
    sendAudioChunk,
    isConnected
  } = useWebSocket();

  // Function to capture and send video frame
  const captureFrame = useCallback(() => {
    if (!videoRef.current || !isConnected || !isRecording) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0);
    
    // Convert to base64 and send
    try {
      const frameData = canvas.toDataURL('image/jpeg', 0.8);
      sendVideoFrame(frameData);
    } catch (err) {
      console.error('Frame capture error:', err);
      onError?.('Failed to capture video frame');
    }
  }, [isConnected, isRecording, sendVideoFrame, onError]);

  // Initialize audio recording
  const startAudioRecording = useCallback(() => {
    if (!streamRef.current || !isConnected) return;

    try {
      const audioTrack = streamRef.current.getAudioTracks()[0];
      const mediaRecorder = new MediaRecorder(new MediaStream([audioTrack]));
      mediaRecorderRef.current = mediaRecorder;

      let audioChunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
        
        // Convert and send audio data
        if (audioChunks.length > 0) {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });
          const reader = new FileReader();
          
          reader.onloadend = () => {
            const base64Audio = reader.result.split(',')[1];
            sendAudioChunk(base64Audio);
            audioChunks = [];
          };
          
          reader.readAsDataURL(blob);
        }
      };

      mediaRecorder.start(AUDIO_CHUNK_SIZE);
    } catch (err) {
      console.error('Audio recording error:', err);
      onError?.('Failed to start audio recording');
    }
  }, [isConnected, sendAudioChunk, onError]);

  // Initialize camera and audio stream
  useEffect(() => {
    const startMedia = async () => {
      try {
        setIsLoading(true);
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: true,
          audio: true 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        streamRef.current = stream;
        setIsLoading(false);
      } catch (err) {
        console.error('Media access error:', err);
        onError?.('Failed to access camera or microphone');
        setIsLoading(false);
      }
    };

    startMedia();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [onError]);

  // Handle recording state changes
  useEffect(() => {
    if (isRecording && isConnected) {
      // Start video capture interval
      captureIntervalRef.current = setInterval(captureFrame, CAPTURE_INTERVAL);
      
      // Start audio recording
      startAudioRecording();
    } else {
      // Cleanup
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
      }
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    }

    return () => {
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
      }
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording, isConnected, captureFrame, startAudioRecording]);

  return (
    <div className="w-full max-w-md p-1 rounded-xl shadow-xl bg-cover bg-center relative">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg z-10">
          <div className="flex flex-col items-center gap-2">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white" />
            <span className="text-white text-sm">Initializing camera...</span>
          </div>
        </div>
      )}
      
      {/* Camera View */}
      <div className="rounded-lg overflow-hidden backdrop-blur-sm bg-black/70 relative">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto"
        />
        
        {/* Recording Indicator */}
        {isRecording && (
          <div className="absolute top-2 right-2 flex items-center gap-2">
            <div className="animate-pulse w-3 h-3 rounded-full bg-red-600" />
            <span className="text-white text-xs">Recording</span>
          </div>
        )}
        
        {/* Connection Status */}
        <div className="absolute bottom-2 left-2 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-white text-xs">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  );
};

CameraStream.propTypes = {
  onError: PropTypes.func,
  isRecording: PropTypes.bool.isRequired
};

export default CameraStream;
