import { useState, useEffect, useCallback } from 'react';
import CameraStream from './CameraStream';
import backgroundImg from '../../assets/background.jpg';
import { useLiveSession } from '../../contexts/LiveSessionContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { WSMessageType } from '../../types/websocket';
import StatusIndicator from './StatusIndicator';

const LiveAnalysis = () => {
  const { state, actions, persistSession } = useLiveSession();
  const [showFeedback, setShowFeedback] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [liveFeedbackText, setLiveFeedbackText] = useState({
    eyeContact: "Waiting for analysis...",
    expressions: "Waiting for analysis...",
    posture: "Waiting for analysis...",
    voice: "Waiting for analysis..."
  });
  const [lastUpdateTime, setLastUpdateTime] = useState('');
  
  // WebSocket connection
  const {
    isConnected,
    connect,
    disconnect,
    registerHandler,
    error: wsError,
    sessionId
  } = useWebSocket();

  // Add this near the top of your component
  useEffect(() => {
    console.log("LiveAnalysis state:", {
      isConnected,
      sessionId,
      recordingStatus: state.status,
      hasFeedback: !!state.feedback
    });
  }, [isConnected, sessionId, state.status, state.feedback]);

  // Handle WebSocket feedback
  const handleFeedback = useCallback((data) => {
    console.log("🔍 Received feedback data:", data);
    
    if (!data) {
      console.warn("Received empty feedback data");
      return;
    }
    
    // Update session feedback state with real data
    actions.updateFeedback({
      speech_rate: {
        wpm: data.gemini_feedback?.voice_feedback ? 
          parseFloat(data.gemini_feedback.voice_feedback.match(/\d+(\.\d+)?/)?.[0] || 0) : 
          null,
        assessment: null,
        suggestion: data.gemini_feedback?.voice_feedback || null
      },
      filler_words: {
        total: 0,
        counts: {},
        suggestion: null
      },
      clarity: {
        score: null,
        suggestion: null
      },
      sentiment: {
        label: data.emotion || null,
        score: null,
        suggestion: data.gemini_feedback?.expression_feedback || null
      },
      keywords: {
        topics: [],
        context: null
      },
      transcript: data.transcript || "",
      raw_feedback: data
    });
    
    // Update live feedback text with real data
    setLiveFeedbackText({
      eyeContact: data.gemini_feedback?.eye_contact_feedback || "Analyzing eye contact...",
      expressions: data.gemini_feedback?.expression_feedback || "Analyzing facial expressions...",
      posture: data.gemini_feedback?.posture_feedback || "Analyzing posture...",
      voice: data.gemini_feedback?.voice_feedback || "Analyzing voice..."
    });
    
    // Show feedback panel and update timestamp for UI refresh
    setShowFeedback(true);
    setLastUpdateTime(new Date().toLocaleTimeString());
  }, [actions]);

  // Register WebSocket handlers
  useEffect(() => {
    registerHandler(WSMessageType.FEEDBACK, handleFeedback);
    registerHandler(WSMessageType.ERROR, (data) => {
      actions.setError(data.error || 'Unknown error');
    });
    
    return () => {
      // No need to unregister as the WebSocket service handles this
    };
  }, [registerHandler, handleFeedback, actions]);

  // Update connection status in context
  useEffect(() => {
    // Only update if the values are different from what's in state
    if (state.isConnected !== isConnected) {
      actions.setConnection(isConnected);
    }
    
    if (sessionId && state.sessionId !== sessionId) {
      actions.setSessionId(sessionId);
    }
  }, [isConnected, sessionId, actions, state.isConnected, state.sessionId]);

  // Handle WebSocket errors
  useEffect(() => {
    if (wsError && state.error !== wsError) {
      actions.setError(wsError);
    }
  }, [wsError, actions, state.error]);

  // Handle camera errors
  const handleCameraError = useCallback((error) => {
    actions.setError(error);
  }, [actions]);

  // Start recording
  const handleStart = useCallback(async () => {
    setIsStarting(true);
    actions.setStatus('recording');
    actions.setError(null);
    
    try {
      await connect();
      console.log('WebSocket connected, session started');
    } catch (error) {
      console.error('Failed to start session:', error);
      actions.setError(`Failed to start session: ${error.message}`);
      actions.setStatus('idle');
      setIsStarting(false);
    }
  }, [connect, actions]);

  // Stop recording
  const handleStop = useCallback(async () => {
    actions.setStatus('stopped');
    await disconnect();
  }, [disconnect, actions]);

  // Handle save session
  const handleSave = useCallback(async () => {
    if (!state.feedback) {
      return;
    }
    
    actions.setLoading(true);
    
    try {
      // Create a simplified version of the feedback for saving
      const sessionData = {
        session_id: sessionId || state.sessionId,
        timestamp: new Date().toISOString(),
        feedback: {
          emotion: state.feedback.sentiment?.label || "neutral",
          eye_contact: "yes", // Default value
          transcript: state.feedback.transcript || "",
          gemini_feedback: {
            posture_feedback: state.feedback.raw_feedback?.gemini_feedback?.posture_feedback || "",
            expression_feedback: state.feedback.raw_feedback?.gemini_feedback?.expression_feedback || "",
            eye_contact_feedback: state.feedback.raw_feedback?.gemini_feedback?.eye_contact_feedback || "",
            voice_feedback: state.feedback.raw_feedback?.gemini_feedback?.voice_feedback || "",
            overall_suggestion: state.feedback.raw_feedback?.gemini_feedback?.overall_suggestion || ""
          }
        }
      };
      
      console.log("Saving session data:", sessionData);
      
      // Use the correct API endpoint for saving sessions
      const response = await fetch('http://localhost:8000/api/live/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      const result = await response.json();
      console.log("Session saved successfully:", result);
      
      // Add to history
      actions.addToHistory({
        timestamp: new Date(),
        data: state.feedback
      });
      
      // Reset session
      actions.resetSession();
      
      // Redirect to dashboard or feedback page
      // setCurrentPage('dashboard');
    } catch (error) {
      console.error("Failed to save session:", error);
      actions.setError(`Failed to save session: ${error.message}`);
    } finally {
      actions.setLoading(false);
    }
  }, [state.feedback, state.sessionId, sessionId, actions]);

  // Discard session
  const handleDiscard = useCallback(() => {
    actions.resetSession();
    setShowFeedback(false);
  }, [actions]);

  return (
    <div
      className="w-full min-h-screen bg-cover bg-center bg-no-repeat p-8 font-mono text-[#030303] flex flex-col items-center"
      style={{ backgroundImage: `url(${backgroundImg})` }}
    >
      {/* Header */}
      <div className="w-full max-w-7xl mb-6 text-center">
        <h1 className="text-4xl font-bold">Live Analysis</h1>
        <StatusIndicator 
          status={state.status === 'idle' ? 'Idle' : 
                 state.status === 'recording' ? 'Recording' : 
                 state.status === 'stopped' ? 'Stopped' : 'Error'}
          isConnected={state.isConnected}
          sessionId={state.sessionId}
        />
        {state.error && (
          <div className="mt-2 text-red-600 bg-red-100 p-2 rounded">
            {state.error}
          </div>
        )}
      </div>

      {/* Layout Row: Camera + Feedback */}
      <div className="w-full max-w-7xl flex flex-col md:flex-row gap-6">
        {/* Camera Feed */}
        <div className="flex-1 flex justify-center">
          <CameraStream 
            onError={handleCameraError}
            isRecording={state.status === 'recording'}
          />
        </div>

        {/* Live Feedback Panel */}
        <div className="flex-1 space-y-4 bg-white/80 backdrop-blur-sm p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Live Feedback</h2>

          {/* Live Feedback - Shown during recording */}
          {state.status === 'recording' && (
            <div className="space-y-4 mt-4">
              <h3 className="text-xl font-semibold">Live Feedback</h3>
              <p className="text-sm text-gray-500">Last updated: {lastUpdateTime || 'Waiting for data...'}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold mb-2">👁️ Eye Contact</h4>
                  <p>{liveFeedbackText.eyeContact}</p>
                </div>
                
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold mb-2">🙂 Facial Expressions</h4>
                  <p>{liveFeedbackText.expressions}</p>
                </div>
                
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold mb-2">🧍 Posture</h4>
                  <p>{liveFeedbackText.posture}</p>
                </div>
                
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold mb-2">🎤 Voice & Clarity</h4>
                  <p>{liveFeedbackText.voice}</p>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Results - Shown after recording is stopped */}
          {showFeedback && state.feedback && state.status !== 'recording' && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Session Summary</h3>
              
              {/* Eye Contact */}
              <div className="p-4 bg-gray-100 rounded-lg">
                <h3 className="font-semibold mb-2">👁️ Eye Contact</h3>
                <p>{state.feedback.raw_feedback?.gemini_feedback?.eye_contact_feedback || "No data available"}</p>
              </div>
              
              {/* Posture */}
              <div className="p-4 bg-gray-100 rounded-lg">
                <h3 className="font-semibold mb-2">🧍 Posture</h3>
                <p>{state.feedback.raw_feedback?.gemini_feedback?.posture_feedback || "No data available"}</p>
              </div>
              
              {/* Voice */}
              <div className="p-4 bg-gray-100 rounded-lg">
                <h3 className="font-semibold mb-2">🎤 Voice & Clarity</h3>
                <p>{state.feedback.raw_feedback?.gemini_feedback?.voice_feedback || "No data available"}</p>
              </div>
              
              {/* Emotion & Sentiment */}
              <div className="p-4 bg-gray-100 rounded-lg">
                <h3 className="font-semibold mb-2">😊 Emotion & Sentiment</h3>
                <p>Detected emotion: {state.feedback.sentiment?.label || "neutral"}</p>
                <p>{state.feedback.raw_feedback?.gemini_feedback?.expression_feedback || "No data available"}</p>
              </div>
              
              {/* Overall Suggestion */}
              <div className="p-4 bg-blue-100 rounded-lg">
                <h3 className="font-semibold mb-2">💡 Overall Suggestion</h3>
                <p>{state.feedback.raw_feedback?.gemini_feedback?.overall_suggestion || "Keep practicing to improve your presentation skills."}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="mt-8 flex flex-wrap justify-center gap-4">
        <button
          onClick={handleStart}
          disabled={state.status === 'recording' || isStarting}
          className={`px-6 py-2 rounded-full font-semibold transition ${
            state.status === 'recording' || isStarting
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {isStarting ? (
            <>
              <span className="animate-pulse">●</span>
              Starting...
            </>
          ) : (
            'Start Analysis'
          )}
        </button>
        <button
          onClick={handleStop}
          disabled={state.status !== 'recording'}
          className={`px-6 py-2 rounded-full font-semibold transition ${
            state.status !== 'recording'
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
        >
          Stop
        </button>
        <button
          onClick={handleSave}
          disabled={!state.feedback || state.isLoading}
          className={`px-6 py-2 rounded-full font-semibold transition ${
            !state.feedback || state.isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {state.isLoading ? 'Saving...' : 'Save Session'}
        </button>
        <button
          onClick={handleDiscard}
          disabled={state.isLoading}
          className="bg-gray-500 text-white px-6 py-2 rounded-full font-semibold hover:bg-gray-600 transition"
        >
          Discard
        </button>
      </div>
    </div>
  );
};

export default LiveAnalysis;
