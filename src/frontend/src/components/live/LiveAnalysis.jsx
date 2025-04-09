import { useState } from 'react';
import CameraStream from './CameraStream';
import backgroundImg from '../../assets/background.jpg';

const LiveAnalysis = () => {
  const [status, setStatus] = useState('Idle');
  const [showFeedback, setShowFeedback] = useState(false);

  const mockFeedbackText = {
    eyeContact: "Maintaining good eye contact with the camera.",
    expressions: "Facial expressions appear engaged and confident.",
    posture: "Posture is upright and consistent.",
    voice: "Voice is clear with a steady pace.",
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

  const statusColor = {
    'Idle': 'bg-gray-400',
    'Recording': 'bg-green-600',
    'Analyzing': 'bg-yellow-500',
    'Finished': 'bg-blue-600',
    'Stopped': 'bg-red-500',
  }[status];

  return (
    <div
      className="w-full min-h-screen bg-cover bg-center bg-no-repeat p-8 font-mono text-[#030303] flex flex-col items-center"
      style={{ backgroundImage: `url(${backgroundImg})` }}
    >
      {/* Header */}
      <div className="w-full max-w-7xl mb-6 text-center">
        <h1 className="text-4xl font-bold">Live Analysis</h1>
        <span className={`inline-block mt-2 px-4 py-1 rounded-full text-white text-sm ${statusColor}`}>
          {status}
        </span>
      </div>

      {/* Layout Row: Camera + Feedback */}
      <div className="w-full max-w-7xl flex flex-col md:flex-row gap-6">
        {/* Camera Feed */}
        <div className="flex-1 flex justify-center">
          <CameraStream />
        </div>

        {/* Feedback Panel */}
        {showFeedback && (
          <div className="flex-1 space-y-4 bg-white/80 backdrop-blur-sm p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-semibold mb-4">Live Feedback</h2>

            {Object.entries(mockFeedbackText).map(([key, value]) => {
              const titles = {
                eyeContact: '👁️ Eye Contact',
                expressions: '🙂 Facial Expressions',
                posture: '🧍 Posture',
                voice: '🎤 Voice & Clarity',
              };
              return (
                <div key={key} className="p-4 bg-gray-100 rounded-lg">
                  <h3 className="font-semibold mb-2">{titles[key]}</h3>
                  <p>{value}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="mt-8 flex flex-wrap justify-center gap-4">
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
    </div>
  );
};

export default LiveAnalysis;
