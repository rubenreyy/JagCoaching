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
  const [feedbackStatus, setFeedbackStatus] = useState({
    eyeContact: "neutral",
    expressions: "neutral",
    posture: "neutral",
    voice: "neutral"
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

  // Add new state for tracking session metrics
  const [sessionMetrics, setSessionMetrics] = useState({
    eyeContact: { good: 0, limited: 0, total: 0 },
    expressions: { positive: 0, neutral: 0, negative: 0, total: 0 },
    posture: { good: 0, poor: 0, total: 0 },
    voice: { good: 0, moderate: 0, poor: 0, total: 0 }
  });

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
        score: null
      },
      eye_contact: {
        score: data.eye_contact === "yes" ? 1 : data.eye_contact === "limited" ? 0.5 : 0,
        suggestion: data.gemini_feedback?.eye_contact_feedback || null
      },
      posture: {
        score: data.posture === "good" ? 1 : data.posture === "poor" ? 0 : 0.5,
        suggestion: data.gemini_feedback?.posture_feedback || null
      },
      raw_feedback: data
    });
    
    // Update live feedback text with more specific messages based on actual status
    const newFeedbackText = {
      // For eye contact, provide more specific guidance
      eyeContact: data.eye_contact === "yes" 
        ? "Great eye contact! You're connecting well with your audience."
        : data.eye_contact === "limited"
        ? "Try looking directly at the camera lens. Position yourself so your eyes are level with the camera."
        : data.gemini_feedback?.eye_contact_feedback || "Looking for eye contact...",
      
      // For expressions, be more specific about the detected emotion
      expressions: data.emotion === "happy"
        ? "Great smile! Your positive expression engages the audience."
        : data.emotion === "neutral"
        ? "Try to add more expression to engage your audience better."
        : data.gemini_feedback?.expression_feedback || "Analyzing expressions...",
      
      // For posture, acknowledge when it's good
      posture: data.posture === "good"
        ? "Excellent posture! You appear confident and professional."
        : data.gemini_feedback?.posture_feedback || "Checking posture...",
      
      // For voice, be more specific about audio quality
      voice: data.audio_quality === "excellent"
        ? "Excellent voice projection! Very clear speech."
        : data.audio_quality === "good"
        ? "Good volume level - your speech is clear and audible."
        : data.audio_quality === "moderate"
        ? "Acceptable volume - try projecting a bit more for clarity."
        : data.audio_quality === "low"
        ? "Volume is low - please speak louder to be heard clearly."
        : data.audio_quality === "none"
        ? "No speech detected - please speak up."
        : data.audio_quality === "too_loud"
        ? "Volume may be too loud - consider speaking a bit softer."
        : data.gemini_feedback?.voice_feedback || "Listening to your voice..."
    };
    
    // Update feedback status indicators
    const newFeedbackStatus = {
      eyeContact: data.eye_contact === "yes" ? "positive" : data.eye_contact === "limited" ? "warning" : "negative",
      expressions: data.emotion === "happy" ? "positive" : data.emotion === "neutral" ? "neutral" : "warning",
      posture: data.posture === "good" ? "positive" : data.posture === "poor" ? "negative" : "neutral",
      voice: data.audio_quality === "good" || data.audio_quality === "excellent" ? "positive" : 
             data.audio_quality === "moderate" ? "neutral" : 
             data.audio_quality === "low" ? "warning" : "negative"
    };
    
    // Track metrics for session summary
    setSessionMetrics(prev => {
      // Update eye contact metrics
      const eyeContact = {...prev.eyeContact};
      if (data.eye_contact === "yes") eyeContact.good++;
      else if (data.eye_contact === "limited") eyeContact.limited++;
      eyeContact.total++;
      
      // Update expressions metrics
      const expressions = {...prev.expressions};
      if (data.emotion === "happy") expressions.positive++;
      else if (data.emotion === "neutral") expressions.neutral++;
      else expressions.negative++;
      expressions.total++;
      
      // Update posture metrics
      const posture = {...prev.posture};
      if (data.posture === "good") posture.good++;
      else if (data.posture === "poor") posture.poor++;
      posture.total++;
      
      // Update voice metrics
      const voice = {...prev.voice};
      if (data.audio_quality === "good" || data.audio_quality === "excellent") voice.good++;
      else if (data.audio_quality === "moderate") voice.moderate++;
      else voice.poor++;
      voice.total++;
      
      return { eyeContact, expressions, posture, voice };
    });
    
    setLiveFeedbackText(newFeedbackText);
    setFeedbackStatus(newFeedbackStatus);
    
    // Update timestamp
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

  // Enhanced handleStop function to generate session summary
  const handleStop = useCallback(async () => {
    if (state.status !== 'recording') {
      return;
    }
    
    actions.setStatus('stopped');
    disconnect();
    
    // Generate session summary based on collected metrics
    const summary = generateSessionSummary(sessionMetrics);
    
    // Update the feedback with the summary
    actions.updateFeedback({
      ...state.feedback,
      session_summary: summary
    });
    
    setShowFeedback(true);
    
  }, [state.status, disconnect, actions, sessionMetrics, state.feedback]);

  // Function to generate session summary
  const generateSessionSummary = useCallback((metrics) => {
    const summary = {};
    
    // Eye contact summary
    const eyeContactRatio = metrics.eyeContact.total > 0 ? 
      metrics.eyeContact.good / metrics.eyeContact.total : 0;
    
    if (eyeContactRatio >= 0.7) {
      summary.eyeContact = {
        status: "positive",
        message: "Excellent eye contact throughout your session. You consistently engaged with the camera."
      };
    } else if (eyeContactRatio >= 0.4) {
      summary.eyeContact = {
        status: "neutral",
        message: "Your eye contact was inconsistent. Try to maintain more consistent eye contact with the camera."
      };
    } else {
      summary.eyeContact = {
        status: "negative",
        message: "Your eye contact needs improvement. Practice looking directly at the camera lens more consistently."
      };
    }
    
    // Expressions summary
    const expressionPositiveRatio = metrics.expressions.total > 0 ? 
      metrics.expressions.positive / metrics.expressions.total : 0;
    const expressionNeutralRatio = metrics.expressions.total > 0 ? 
      metrics.expressions.neutral / metrics.expressions.total : 0;
    
    if (expressionPositiveRatio >= 0.6) {
      summary.expressions = {
        status: "positive",
        message: "Great facial expressions! You showed positive engagement throughout your presentation."
      };
    } else if (expressionNeutralRatio >= 0.7) {
      summary.expressions = {
        status: "neutral",
        message: "Your expressions were mostly neutral. Try to add more varied expressions to engage your audience."
      };
    } else {
      summary.expressions = {
        status: "warning",
        message: "Your expressions could use improvement. Practice showing more positive and engaging expressions."
      };
    }
    
    // Posture summary
    const postureRatio = metrics.posture.total > 0 ? 
      metrics.posture.good / metrics.posture.total : 0;
    
    if (postureRatio >= 0.7) {
      summary.posture = {
        status: "positive",
        message: "Excellent posture throughout your presentation. You appeared confident and professional."
      };
    } else if (postureRatio >= 0.4) {
      summary.posture = {
        status: "neutral",
        message: "Your posture was inconsistent. Remember to maintain good posture throughout your presentation."
      };
    } else {
      summary.posture = {
        status: "negative",
        message: "Your posture needs improvement. Practice standing/sitting straight with shoulders back."
      };
    }
    
    // Voice summary
    const voiceRatio = metrics.voice.total > 0 ? 
      metrics.voice.good / metrics.voice.total : 0;
    
    if (voiceRatio >= 0.7) {
      summary.voice = {
        status: "positive",
        message: "Excellent voice projection and clarity throughout your presentation."
      };
    } else if (voiceRatio >= 0.4) {
      summary.voice = {
        status: "neutral",
        message: "Your voice projection was inconsistent. Practice maintaining consistent volume and clarity."
      };
    } else {
      summary.voice = {
        status: "negative",
        message: "Your voice projection needs improvement. Practice speaking louder and more clearly."
      };
    }
    
    // Overall summary
    const overallScore = (eyeContactRatio + expressionPositiveRatio + postureRatio + voiceRatio) / 4;
    
    if (overallScore >= 0.7) {
      summary.overall = {
        status: "positive",
        message: "Great job! You demonstrated strong presentation skills overall. Keep up the good work!"
      };
    } else if (overallScore >= 0.4) {
      summary.overall = {
        status: "neutral",
        message: "Your presentation skills are developing well. Focus on consistency in all areas for improvement."
      };
    } else {
      summary.overall = {
        status: "warning",
        message: "Your presentation skills need more practice. Focus on the specific areas highlighted for improvement."
      };
    }
    
    return summary;
  }, []);

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
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg ${feedbackStatus.eyeContact === 'positive' ? 'bg-green-100' : feedbackStatus.eyeContact === 'warning' ? 'bg-yellow-100' : feedbackStatus.eyeContact === 'negative' ? 'bg-red-100' : 'bg-gray-100'}`}>
                <h3 className="font-semibold mb-2">👁️ Eye Contact</h3>
                <p>{liveFeedbackText.eyeContact}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${feedbackStatus.expressions === 'positive' ? 'bg-green-100' : feedbackStatus.expressions === 'warning' ? 'bg-yellow-100' : feedbackStatus.expressions === 'negative' ? 'bg-red-100' : 'bg-gray-100'}`}>
                <h3 className="font-semibold mb-2">😊 Expressions</h3>
                <p>{liveFeedbackText.expressions}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${feedbackStatus.posture === 'positive' ? 'bg-green-100' : feedbackStatus.posture === 'warning' ? 'bg-yellow-100' : feedbackStatus.posture === 'negative' ? 'bg-red-100' : 'bg-gray-100'}`}>
                <h3 className="font-semibold mb-2">🧍 Posture</h3>
                <p>{liveFeedbackText.posture}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${feedbackStatus.voice === 'positive' ? 'bg-green-100' : feedbackStatus.voice === 'warning' ? 'bg-yellow-100' : feedbackStatus.voice === 'negative' ? 'bg-red-100' : 'bg-gray-100'}`}>
                <h3 className="font-semibold mb-2">🔊 Voice</h3>
                <p>{liveFeedbackText.voice}</p>
              </div>
              
              <div className="col-span-1 md:col-span-2 text-xs text-gray-500 text-right">
                Last updated: {lastUpdateTime || 'Not yet'}
              </div>
            </div>
          )}

          {/* Analysis Results - Shown after recording is stopped */}
          {showFeedback && state.feedback && state.feedback.session_summary && state.status !== 'recording' && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Session Summary</h3>
              
              {/* Eye Contact Summary */}
              <div className={`p-4 rounded-lg ${
                state.feedback.session_summary.eyeContact.status === 'positive' ? 'bg-green-100' : 
                state.feedback.session_summary.eyeContact.status === 'neutral' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <h3 className="font-semibold mb-2">👁️ Eye Contact</h3>
                <p>{state.feedback.session_summary.eyeContact.message}</p>
              </div>
              
              {/* Expressions Summary */}
              <div className={`p-4 rounded-lg ${
                state.feedback.session_summary.expressions.status === 'positive' ? 'bg-green-100' : 
                state.feedback.session_summary.expressions.status === 'neutral' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <h3 className="font-semibold mb-2">😊 Expressions</h3>
                <p>{state.feedback.session_summary.expressions.message}</p>
              </div>
              
              {/* Posture Summary */}
              <div className={`p-4 rounded-lg ${
                state.feedback.session_summary.posture.status === 'positive' ? 'bg-green-100' : 
                state.feedback.session_summary.posture.status === 'neutral' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <h3 className="font-semibold mb-2">🧍 Posture</h3>
                <p>{state.feedback.session_summary.posture.message}</p>
              </div>
              
              {/* Voice Summary */}
              <div className={`p-4 rounded-lg ${
                state.feedback.session_summary.voice.status === 'positive' ? 'bg-green-100' : 
                state.feedback.session_summary.voice.status === 'neutral' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <h3 className="font-semibold mb-2">🔊 Voice</h3>
                <p>{state.feedback.session_summary.voice.message}</p>
              </div>
              
              {/* Overall Summary */}
              <div className={`p-4 rounded-lg ${
                state.feedback.session_summary.overall.status === 'positive' ? 'bg-blue-100' : 
                state.feedback.session_summary.overall.status === 'neutral' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <h3 className="font-semibold mb-2">💡 Overall Assessment</h3>
                <p>{state.feedback.session_summary.overall.message}</p>
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
