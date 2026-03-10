import { useEffect, useRef, useState, useCallback } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import PropTypes from 'prop-types';

const CameraStream = ({ onError, isRecording }) => {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(document.createElement('canvas'));
  const captureIntervalRef = useRef(null);
  const audioContextRef = useRef(null);
  
  const [cameraInitialized, setCameraInitialized] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  
  const { sendMessage, isConnected } = useWebSocket();
  
  // Log state changes for debugging
  useEffect(() => {
    console.log(`Video recording state changed: ${isRecording}, Connected: ${isConnected}`);
  }, [isRecording, isConnected]);

  // Function to capture and send a video frame
  const captureAndSendFrame = useCallback(() => {
    if (!videoRef.current || !cameraInitialized) return;
    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw the current video frame to the canvas
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to base64 and send
      const imageData = canvas.toDataURL('image/jpeg', 0.7);
      
      console.log('Sending video frame to server');
      sendMessage({
        type: 'video_frame',
        data: imageData
      });
    } catch (error) {
      console.error('Error capturing video frame:', error);
    }
  }, [cameraInitialized, sendMessage]);

  // Initialize media devices
  const initializeMedia = useCallback(async () => {
    if (!isRecording || !isConnected) {
      console.log('Not recording or not connected, skipping media initialization');
      return;
    }

    try {
      console.log('Initializing camera...');
      
      // Stop any existing streams
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      // Request camera access with explicit constraints
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: true
      });
      
      console.log('Camera access granted!');
      
      // Store the stream for later cleanup
      streamRef.current = stream;
      
      // Set the video source
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded, starting playback');
          videoRef.current.play()
            .then(() => {
              console.log('Video playback started successfully');
              setCameraInitialized(true);
              
              // Start capturing frames
              if (captureIntervalRef.current) {
                clearInterval(captureIntervalRef.current);
              }
              
              captureIntervalRef.current = setInterval(() => {
                captureAndSendFrame();
              }, 1000);
            })
            .catch(err => {
              console.error('Error starting video playback:', err);
              setCameraError('Failed to start video playback');
              if (onError) onError(err);
            });
        };
      }
    } catch (err) {
      console.error('Error initializing media:', err);
      setCameraError(err.message || 'Failed to access camera');
      if (onError) onError(err);
    }
  }, [isRecording, isConnected, captureAndSendFrame, onError]);

  // Stop capturing
  const stopCapturing = useCallback(() => {
    console.log('Stopping capture...');
    
    // Clear intervals
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current);
      captureIntervalRef.current = null;
    }
    
    // Stop all tracks in the stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // Clear video source
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setCameraInitialized(false);
  }, []);

  // Initialize or clean up based on recording state
  useEffect(() => {
    if (isRecording && isConnected) {
      // Add a small delay to ensure WebSocket is fully connected
      const timer = setTimeout(() => {
        initializeMedia();
      }, 500);
      
      return () => clearTimeout(timer);
    } else {
      stopCapturing();
    }
  }, [isRecording, isConnected, initializeMedia, stopCapturing]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopCapturing();
    };
  }, [stopCapturing]);

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
      {!cameraInitialized && isRecording && (
        <div className="absolute inset-0 flex items-center justify-center text-white">
          Initializing camera...
        </div>
      )}
      
      {cameraError && (
        <div className="absolute inset-0 flex items-center justify-center text-red-500 bg-black bg-opacity-75 p-4">
          Error: {cameraError}
        </div>
      )}
      
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        autoPlay
        playsInline
        muted
      />
    </div>
  );
};

CameraStream.propTypes = {
  onError: PropTypes.func,
  isRecording: PropTypes.bool.isRequired
};

export default CameraStream; 