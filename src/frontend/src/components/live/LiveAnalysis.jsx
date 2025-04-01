import { useState } from 'react';
import CameraStream from './CameraStream';
import Feedback from '../feedback/Feedback';
import backgroundImg from '../../assets/background.jpg';

const LiveAnalysis = () => {
  const [status, setStatus] = useState('Idle');
  const [showFeedback, setShowFeedback] = useState(false);

  const mockFeedbackData = {
    speech_rate: {
      wpm: 130,
      assessment: 'Good',
      suggestion: 'Keep the current pace.',
    },
    filler_words: {
      total: 2,
      counts: { like: 1, um: 1 },
      suggestion: 'Try to reduce filler words further.',
    },
    clarity: {
      score: 89,
      suggestion: 'Great clarity!',
    },
    sentiment: {
      label: 'Positive',
      score: 0.85,
      suggestion: 'You sound confident and friendly.',
    },
    keywords: {
      topics: ['project', 'results', 'teamwork'],
      context: 'You emphasized key areas well.',
    },
  };

  const handleStart = () => {
    setStatus('Recording');
    setShowFeedback(false);

    setTimeout(() => {
      setStatus('Analyzing');
      setTimeout(() => {
        setStatus('Finished');
        setShowFeedback(true);
      }, 2000);
    }, 3000);
  };

  const handleStop = () => setStatus('Stopped');
  const handleSave = () => alert('Session saved!');
  const handleDiscard = () => {
    setShowFeedback(false);
    setStatus('Idle');
  };

  return (
    <div
      className="w-full min-h-screen bg-cover bg-center bg-no-repeat flex flex-col items-center justify-start p-8 font-mono text-[#030303]"
      style={{
        backgroundImage: `url(${backgroundImg})`,
      }}
    >
      {/* Header + Status */}
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold mb-2">Live Analysis</h1>
        <span
          className={`px-4 py-1 rounded-full text-white text-sm ${
            status === 'Recording'
              ? 'bg-green-600'
              : status === 'Analyzing'
              ? 'bg-yellow-500'
              : status === 'Finished'
              ? 'bg-blue-600'
              : 'bg-gray-400'
          }`}
        >
          {status}
        </span>
      </div>

      {/* Camera */}
      <div className="flex justify-center mb-6">
        <CameraStream />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap justify-center gap-4 mb-6">
        <button
          onClick={handleStart}
          className="bg-green-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-green-700 transition"
        >
          Start Analysis
        </button>
        <button
          onClick={handleStop}
          className="bg-red-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-red-700 transition"
        >
          Stop
        </button>
        <button
          onClick={handleSave}
          className="bg-blue-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-blue-700 transition"
        >
          Save Session
        </button>
        <button
          onClick={handleDiscard}
          className="bg-gray-500 text-white px-6 py-2 rounded-full font-semibold hover:bg-gray-600 transition"
        >
          Discard
        </button>
      </div>

      {/* Real-Time Feedback */}
      {showFeedback && (
        <div className="mt-8 w-full max-w-5xl">
          <Feedback feedbackData={mockFeedbackData} />
        </div>
      )}
    </div>
  );
};

export default LiveAnalysis;
