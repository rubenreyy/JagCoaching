import { useEffect, useRef, useState, useCallback } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import PropTypes from 'prop-types';
import { WSMessageType } from '../../types/websocket';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';

const CAPTURE_INTERVAL = 1000; // Capture frame every 1 second
const AUDIO_CHUNK_SIZE = 3000; // Send audio every 3 seconds

const CameraStream = ({ onError, isRecording }) => {
  // Add performance monitoring
  usePerformanceMonitor('CameraStream');
  
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(document.createElement('canvas'));
  const captureIntervalRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioIntervalRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  
  const [cameraInitialized, setCameraInitialized] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  
  const { sendVideoFrame, sendAudioChunk, isConnected } = useWebSocket();
  
  // Log state changes for debugging
  useEffect(() => {
    console.log(`Video recording state changed: ${isRecording}, Connected: ${isConnected}`);
  }, [isRecording, isConnected]);

  // Initialize camera immediately when component mounts
  useEffect(() => {
    const startCamera = async () => {
      try {
        console.log('Starting camera...');
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: true,
          audio: true
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          setCameraInitialized(true);
          console.log('Camera initialized successfully');
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
        setCameraError(err.message || 'Failed to access camera');
        if (onError) onError(err.message || 'Failed to access camera');
      }
    };
    
    startCamera();
    
    return () => {
      console.log('Cleaning up camera resources...');
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, [onError]);

  // Initialize canvas ref if it doesn't exist
  useEffect(() => {
    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }
  }, []);

  // Capture a frame from the video stream and send it to the server
  const captureAndSendFrame = useCallback(() => {
    if (!videoRef.current || !streamRef.current) {
      console.warn('Video or stream not initialized');
      return;
    }
    
    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }
    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      
      // Draw the current video frame to the canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Get the image data as base64 string
      const frameData = canvas.toDataURL('image/jpeg', 0.7);
      
      // Log the size of the data being sent
      console.log(`Sending frame data: ${Math.round(frameData.length / 1024)} KB`);
      
      // Send the frame data to the server - IMPORTANT: Don't check isConnected here
      sendVideoFrame(frameData);
    } catch (error) {
      console.error('Error capturing frame:', error);
    }
  }, [sendVideoFrame]);

  // Send collected audio data to the server
  const sendAudioData = useCallback(() => {
    try {
      if (audioChunksRef.current.length === 0) {
        console.log('No audio chunks to send');
        return;
      }
      
      console.log(`Preparing to send ${audioChunksRef.current.length} audio chunks`);
      
      // Create a blob from the audio chunks
      const audioBlob = new Blob(audioChunksRef.current);
      console.log(`Audio blob size: ${audioBlob.size} bytes`);
      
      // Convert blob to base64
      const reader = new FileReader();
      
      reader.onloadend = () => {
        const base64Audio = reader.result;
        console.log(`Sending audio chunk: ${Math.round(base64Audio.length / 1024)} KB`);
        
        // Send the audio data to the server if connected
        if (isConnected) {
          sendAudioChunk(base64Audio);
        } else {
          console.log('Not sending audio: WebSocket not connected');
        }
        
        // Clear the audio chunks after sending
        audioChunksRef.current = [];
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error sending audio data:', error);
    }
  }, [sendAudioChunk, isConnected]);

  // Start/stop recording based on isRecording prop
  useEffect(() => {
    if (isRecording) {
      console.log('Starting recording...');
      
      // Start capturing frames at regular intervals
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
      }
      
      captureIntervalRef.current = setInterval(() => {
        captureAndSendFrame();
      }, CAPTURE_INTERVAL);
      
      // Start audio recording if we have a stream
      if (streamRef.current && !mediaRecorderRef.current) {
        try {
          console.log('Setting up audio recording...');
          
          // Get audio track from the stream
          const audioTracks = streamRef.current.getAudioTracks();
          console.log('Audio tracks found:', audioTracks.length);
          
          if (audioTracks.length === 0) {
            console.warn('No audio tracks found in stream');
            return;
          }
          
          // Try different MIME types
          const mimeTypes = [
            'audio/webm',
            'audio/webm;codecs=opus',
            'audio/mp4',
            'audio/ogg;codecs=opus'
          ];
          
          let selectedMimeType = null;
          
          for (const mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
              selectedMimeType = mimeType;
              break;
            }
          }
          
          if (!selectedMimeType) {
            console.error('No supported MIME type found for MediaRecorder');
            return;
          }
          
          console.log(`Using MIME type: ${selectedMimeType}`);
          
          // Create a new MediaRecorder with the full stream (not just audio)
          // This can help with compatibility issues on some browsers
          const mediaRecorder = new MediaRecorder(streamRef.current, {
            mimeType: selectedMimeType,
            audioBitsPerSecond: 128000
          });
          
          // Set up event handlers
          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              audioChunksRef.current.push(event.data);
              console.log(`Audio chunk received: ${event.data.size} bytes`);
            }
          };
          
          mediaRecorder.onstop = () => {
            console.log('Media recorder stopped');
          };
          
          // Clear any existing audio chunks
          audioChunksRef.current = [];
          
          // Start recording
          mediaRecorder.start(1000); // Request data every 1 second
          mediaRecorderRef.current = mediaRecorder;
          
          // Set up interval to send audio chunks
          if (audioIntervalRef.current) {
            clearInterval(audioIntervalRef.current);
          }
          
          audioIntervalRef.current = setInterval(() => {
            if (audioChunksRef.current.length > 0) {
              sendAudioData();
            }
          }, 3000); // Send audio every 3 seconds
          
        } catch (error) {
          console.error('Error starting recording:', error);
          if (onError) onError('Failed to start audio recording: ' + error.message);
        }
      }
    } else {
      console.log('Stopping recording...');
      
      // Stop capturing frames
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
        captureIntervalRef.current = null;
      }
      
      // Stop audio interval
      if (audioIntervalRef.current) {
        clearInterval(audioIntervalRef.current);
        audioIntervalRef.current = null;
      }
      
      // Stop audio recording
      if (mediaRecorderRef.current) {
        try {
          const mediaRecorder = mediaRecorderRef.current;
          
          if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
          }
          
          // Send any remaining audio data
          if (audioChunksRef.current.length > 0) {
            sendAudioData();
          }
        } catch (error) {
          console.warn('Error stopping media recorder:', error);
        }
        mediaRecorderRef.current = null;
      }
    }
    
    return () => {
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
      }
      
      if (audioIntervalRef.current) {
        clearInterval(audioIntervalRef.current);
      }
    };
  }, [isRecording, isConnected, captureAndSendFrame, sendAudioData, onError]);

  return (
    <div className="relative w-full h-full">
      {!cameraInitialized && (
        <div className="absolute inset-0 flex items-center justify-center text-white bg-black rounded-lg">
          Initializing camera...
        </div>
      )}
      
      {cameraError && (
        <div className="absolute inset-0 flex items-center justify-center text-red-500 bg-black bg-opacity-75 p-4 rounded-lg">
          Error: {cameraError}
        </div>
      )}
      
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="rounded-xl shadow-xl object-cover w-full"
        style={{
          maxWidth: '900px',
          aspectRatio: '4 / 3',
          backgroundColor: 'black',
          border: 'none',
        }}
      />
      
      {/* Recording indicator */}
      {cameraInitialized && isRecording && (
        <div className="absolute top-2 right-2 flex items-center gap-2">
          <div className="animate-pulse w-3 h-3 rounded-full bg-red-600"></div>
          <span className="text-white text-xs font-medium">Recording</span>
        </div>
      )}
      
      {/* Connection status indicator */}
      {isRecording && !isConnected && (
        <div className="absolute bottom-2 left-2 bg-yellow-600 text-white px-2 py-1 rounded text-xs">
          Demo Mode (Server Unavailable)
        </div>
      )}
    </div>
  );
};

CameraStream.propTypes = {
  onError: PropTypes.func,
  isRecording: PropTypes.bool.isRequired
};

export default CameraStream;
