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
        // Request audio with specific constraints for better sensitivity
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: true,
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            // Increase sensitivity
            volume: 1.0,
            sampleRate: 44100,
            sampleSize: 16
          }
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

  // Ensure audio chunks are being collected
  useEffect(() => {
    if (isRecording && mediaRecorderRef.current) {
      // Log audio collection status
      console.log('Audio recording active:', 
        mediaRecorderRef.current.state === 'recording',
        'Chunks:', audioChunksRef.current.length);
      
      // Make sure we're collecting audio data
      if (mediaRecorderRef.current.state !== 'recording') {
        try {
          mediaRecorderRef.current.start(1000);
          console.log('Restarted audio recording');
        } catch (err) {
          console.error('Error restarting audio recording:', err);
        }
      }
    }
  }, [isRecording]);

  // Improved audio sending function
  const sendAudioChunks = useCallback(() => {
    if (!isRecording || !isConnected || audioChunksRef.current.length === 0) {
      return;
    }
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      console.log(`Preparing to send audio: ${(audioBlob.size / 1024).toFixed(2)} KB`);
      
      if (audioBlob.size > 0) {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Audio = reader.result;
          sendAudioChunk(base64Audio);
          console.log(`Sent audio chunk: ${(base64Audio.length / 1024).toFixed(2)} KB`);
          // Clear chunks after sending
          audioChunksRef.current = [];
        };
        reader.readAsDataURL(audioBlob);
      }
    } catch (err) {
      console.error('Error sending audio chunks:', err);
    }
  }, [isRecording, isConnected, sendAudioChunk]);

  // Set up audio sending interval
  useEffect(() => {
    if (isRecording && isConnected) {
      if (audioIntervalRef.current) {
        clearInterval(audioIntervalRef.current);
      }
      
      audioIntervalRef.current = setInterval(() => {
        sendAudioChunks();
      }, AUDIO_CHUNK_SIZE);
      
      return () => {
        if (audioIntervalRef.current) {
          clearInterval(audioIntervalRef.current);
          audioIntervalRef.current = null;
        }
      };
    }
  }, [isRecording, isConnected, sendAudioChunks]);

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
          
          // Try to increase audio gain if possible
          try {
            const audioTrack = audioTracks[0];
            const capabilities = audioTrack.getCapabilities();
            console.log('Audio capabilities:', capabilities);
            
            if (capabilities && capabilities.volume) {
              const constraints = { volume: 1.0 }; // Max volume
              audioTrack.applyConstraints({ advanced: [constraints] })
                .then(() => console.log('Applied audio constraints successfully'))
                .catch(err => console.warn('Could not apply audio constraints:', err));
            }
          } catch (err) {
            console.warn('Error adjusting audio track settings:', err);
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
          
          // Create a new MediaRecorder with higher bitrate for better quality
          const mediaRecorder = new MediaRecorder(streamRef.current, {
            mimeType: selectedMimeType,
            audioBitsPerSecond: 256000  // Increased from 128000
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
      
      // Stop audio recording
      if (mediaRecorderRef.current) {
        try {
          const mediaRecorder = mediaRecorderRef.current;
          
          if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
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
    };
  }, [isRecording, isConnected, captureAndSendFrame, onError]);

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
