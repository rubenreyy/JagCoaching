import { useState, useEffect, useCallback } from 'react';
import CameraStream from './CameraStream';
import Feedback from '../feedback/Feedback';
import StatusIndicator from './StatusIndicator';
import { useLiveSession } from '../../contexts/LiveSessionContext';
import backgroundImg from '../../assets/background.jpg';
import { useWebSocket } from '../../hooks/useWebSocket';
import { WSMessageType } from '../../types/websocket';

const LiveAnalysis = () => {
  const { state, actions, persistSession } = useLiveSession();
  
  // WebSocket connection
  const {
    isConnected,
    connect,
    disconnect,
    registerHandler,
    error: wsError,
    sessionId
  } = useWebSocket();

  // Handle WebSocket feedback
  const handleFeedback = useCallback((data) => {
    actions.setFeedbackData(prevData => {
      // Merge new feedback with existing data
      const newData = {
        speech_rate: {
          wpm: data.wpm || prevData?.speech_rate?.wpm,
          assessment: data.speech_rate?.assessment || prevData?.speech_rate?.assessment,
          suggestion: data.speech_rate?.suggestion || prevData?.speech_rate?.suggestion,
        },
        filler_words: {
          total: data.filler_words?.total || prevData?.filler_words?.total || 0,
          counts: { ...prevData?.filler_words?.counts, ...data.filler_words?.counts },
          suggestion: data.filler_words?.suggestion || prevData?.filler_words?.suggestion,
        },
        clarity: {
          score: data.clarity?.score || prevData?.clarity?.score,
          suggestion: data.clarity?.suggestion || prevData?.clarity?.suggestion,
        },
        sentiment: {
          label: data.emotion || prevData?.sentiment?.label,
          score: data.sentiment?.score || prevData?.sentiment?.score,
          suggestion: data.gemini_feedback?.sentiment || prevData?.sentiment?.suggestion,
        },
        keywords: {
          topics: data.keywords?.topics || prevData?.keywords?.topics || [],
          context: data.gemini_feedback?.context || prevData?.keywords?.context,
        },
      };

      // Add to session history
      actions.setSessionHistory(prev => [...prev, { timestamp: new Date(), data: newData }]);
      return newData;
    });
  }, [actions]);

  // Initialize WebSocket handlers
  useEffect(() => {
    registerHandler(WSMessageType.FEEDBACK, handleFeedback);
    registerHandler(WSMessageType.ERROR, (error) => {
      actions.setError(`Analysis error: ${error}`);
      actions.setStatus('Error');
    });
  }, [registerHandler, handleFeedback, actions]);

  // Handle session start
  const handleStart = async () => {
    try {
      actions.setLoading(true);
      actions.setError(null);
      await connect();
      actions.setStatus('Recording');
    } catch (err) {
      actions.setError(`Failed to start session: ${err.message}`);
    } finally {
      actions.setLoading(false);
    }
  };

  // Handle session stop
  const handleStop = async () => {
    try {
      actions.setStatus('Stopped');
      await disconnect();
    } catch (err) {
      actions.setError(`Failed to stop session: ${err.message}`);
    }
  };

  // Handle session save
  const handleSave = async () => {
    try {
      actions.setLoading(true);
      await persistSession();
      alert('Session saved successfully!');
    } catch (err) {
      actions.setError(`Failed to save session: ${err.message}`);
    } finally {
      actions.setLoading(false);
    }
  };

  // Handle session discard
  const handleDiscard = async () => {
    try {
      await disconnect();
      actions.setShowFeedback(false);
      actions.setStatus('Idle');
      actions.setFeedbackData(null);
      actions.setSessionHistory([]);
      actions.setError(null);
    } catch (err) {
      actions.setError(`Failed to discard session: ${err.message}`);
    }
  };

  return (
    <div
      className="w-full min-h-screen bg-cover bg-center bg-no-repeat flex flex-col items-center justify-start p-8 font-mono text-[#030303]"
      style={{ backgroundImage: `url(${backgroundImg})` }}
    >
      {/* Header + Status */}
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold mb-2">Live Analysis</h1>
        <StatusIndicator 
          status={state.status}
          isConnected={state.isConnected}
          sessionId={state.sessionId}
        />
      </div>

      {/* Progress Bar */}
      {state.isLoading && (
        <div className="w-full max-w-md h-1 mb-4">
          <div className="h-full bg-blue-600 animate-pulse rounded-full" />
        </div>
      )}

      {/* Error Display */}
      {state.error && (
        <div className="w-full max-w-md mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {state.error}
        </div>
      )}

      {/* Camera */}
      <div className="flex justify-center mb-6">
        <CameraStream
          isRecording={state.status === 'Recording'}
          onError={actions.setError}
        />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap justify-center gap-4 mb-6">
        <button
          onClick={handleStart}
          disabled={state.isLoading || state.status === 'Recording'}
          className={`px-6 py-2 rounded-full font-semibold transition flex items-center gap-2 ${
            state.isLoading || state.status === 'Recording'
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {state.isLoading ? (
            <>
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
              Starting...
            </>
          ) : (
            'Start Analysis'
          )}
        </button>
        <button
          onClick={handleStop}
          disabled={state.status !== 'Recording'}
          className={`px-6 py-2 rounded-full font-semibold transition ${
            state.status !== 'Recording'
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

      {/* Feedback Display */}
      {state.showFeedback && state.feedback && (
        <div className="mt-8 w-full max-w-5xl">
          <Feedback 
            feedbackData={state.feedback}
            isLive={state.status === 'Recording'}
          />
        </div>
      )}
    </div>
  );
};

export default LiveAnalysis;
