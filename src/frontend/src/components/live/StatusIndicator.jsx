import PropTypes from 'prop-types';

const StatusIndicator = ({ status, isConnected, sessionId }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'Recording':
        return 'bg-green-600';
      case 'Stopped':
        return 'bg-yellow-500';
      case 'Error':
        return 'bg-red-600';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="flex items-center gap-2">
        <span className={`px-4 py-1 rounded-full text-white text-sm ${getStatusColor()}`}>
          {status}
        </span>
        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>
      {sessionId && (
        <span className="text-xs text-gray-600">Session ID: {sessionId}</span>
      )}
    </div>
  );
};

StatusIndicator.propTypes = {
  status: PropTypes.string.isRequired,
  isConnected: PropTypes.bool.isRequired,
  sessionId: PropTypes.string
};

export default StatusIndicator; 