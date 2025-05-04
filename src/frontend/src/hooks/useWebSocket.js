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

  const sendMessage = useCallback((message) => {
    if (!wsService.socket || wsService.socket.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket is not connected, cannot send message');
      return;
    }
    
    try {
      wsService.socket.send(JSON.stringify(message));
      console.log(`Sent message of type: ${message.type}`);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }, []);

  const sendVideoFrame = useCallback(async (frameData) => {
    try {
      console.log(`Sending video frame, data length: ${frameData.length}`);
      
      wsService.sendVideoFrame(frameData);
      
      console.log('Video frame sent successfully');
    } catch (error) {
      console.error('Error sending video frame:', error);
    }
  }, []);

  const sendAudioChunk = useCallback(async (audioData) => {
    try {
      console.log(`Sending audio chunk, data length: ${audioData.length}`);
      
      wsService.sendAudioChunk(audioData);
      
      console.log('Audio chunk sent successfully');
    } catch (error) {
      console.error('Error sending audio chunk:', error);
    }
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