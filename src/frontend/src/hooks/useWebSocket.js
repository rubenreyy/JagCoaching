import { useState, useEffect, useCallback } from 'react';
import wsService from '../services/websocketService';
import { WSMessageType } from '../types/websocket';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const connect = useCallback(async () => {
    try {
      setError(null);
      await wsService.connect(
        () => setIsConnected(true),
        () => setIsConnected(false)
      );
      setSessionId(wsService.sessionId);
    } catch (err) {
      setError(err.message);
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(async () => {
    try {
      await wsService.disconnect();
      setIsConnected(false);
      setSessionId(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const registerHandler = useCallback((type, handler) => {
    wsService.registerHandler(type, handler);
  }, []);

  const sendVideoFrame = useCallback((frame) => {
    wsService.sendVideoFrame(frame);
  }, []);

  const sendAudioChunk = useCallback((audio) => {
    wsService.sendAudioChunk(audio);
  }, []);

  useEffect(() => {
    // Register ping handler
    wsService.registerHandler(WSMessageType.PING, () => {
      wsService.sendPong();
    });

    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    error,
    sessionId,
    connect,
    disconnect,
    registerHandler,
    sendVideoFrame,
    sendAudioChunk,
  };
}; 