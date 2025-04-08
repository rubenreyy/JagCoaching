import { useEffect, useState } from 'react';

const NetworkMonitor = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionSpeed, setConnectionSpeed] = useState(null);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check connection speed
    const checkSpeed = async () => {
      if ('connection' in navigator) {
        const connection = navigator.connection;
        setConnectionSpeed(connection.effectiveType);
        
        connection.addEventListener('change', () => {
          setConnectionSpeed(connection.effectiveType);
        });
      }
    };

    checkSpeed();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOnline) {
    return (
      <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow">
        You are offline
      </div>
    );
  }

  return null;
};

export default NetworkMonitor; 