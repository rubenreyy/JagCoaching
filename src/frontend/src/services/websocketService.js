import { WSMessageType } from '../types/websocket';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = 1000; // Start with 1 second
    this.handlers = new Map();
    this.isConnecting = false;
  }

  async initSession() {
    try {
      const response = await fetch('http://localhost:8000/api/live/session/start', {
        method: 'POST',
      });
      const data = await response.json();
      this.sessionId = data.session_id;
      return this.sessionId;
    } catch (error) {
      console.error('Failed to initialize session:', error);
      throw error;
    }
  }

  async connect(onConnect, onDisconnect) {
    if (this.isConnecting) return;
    this.isConnecting = true;

    try {
      if (!this.sessionId) {
        await this.initSession();
      }

      this.ws = new WebSocket(`ws://localhost:8000/api/live/ws/${this.sessionId}`);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.reconnectTimeout = 1000;
        this.isConnecting = false;
        onConnect?.();
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        onDisconnect?.();
        this.handleReconnect(onConnect, onDisconnect);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

    } catch (error) {
      console.error('Connection error:', error);
      this.isConnecting = false;
      throw error;
    }
  }

  handleReconnect(onConnect, onDisconnect) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnectTimeout *= 2; // Exponential backoff
      this.connect(onConnect, onDisconnect);
    }, this.reconnectTimeout);
  }

  registerHandler(type, handler) {
    this.handlers.set(type, handler);
  }

  removeHandler(type) {
    this.handlers.delete(type);
  }

  handleMessage(message) {
    const handler = this.handlers.get(message.type);
    if (handler) {
      handler(message.data);
    }
  }

  sendMessage(type, data) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return;
    }

    const message = JSON.stringify({ type, ...data });
    this.ws.send(message);
  }

  sendVideoFrame(frame) {
    this.sendMessage(WSMessageType.VIDEO_FRAME, { frame });
  }

  sendAudioChunk(audio) {
    this.sendMessage(WSMessageType.AUDIO_CHUNK, { audio });
  }

  sendPong() {
    this.sendMessage(WSMessageType.PONG, {});
  }

  async disconnect() {
    if (this.sessionId) {
      try {
        await fetch(`http://localhost:8000/api/live/session/${this.sessionId}/stop`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Error stopping session:', error);
      }
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.sessionId = null;
    this.handlers.clear();
  }
}

// Create a singleton instance
const wsService = new WebSocketService();
export default wsService; 