import { WSMessageType } from '../types/websocket';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.isConnecting = false;
    this.handlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.mockMode = false;
    this.port = 80; // Default port for local development
    // Use IPv4 localhost explicitly
    this.apiBaseUrl = import.meta.env.VITE_API_URL || `http://127.0.0.1:${this.port}`;
  }

  async connect(onConnect, onDisconnect) {
    // If already connecting or connected, disconnect first
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      await this.disconnect();
    }

    this.isConnecting = true;

    return new Promise(async (resolve, reject) => {
      let timeoutId;
      let settled = false; // Prevent multiple resolve/reject

      function safeResolve(...args) {
        if (!settled) {
          settled = true;
          clearTimeout(timeoutId);
          resolve(...args);
        }
      }
      function safeReject(...args) {
        if (!settled) {
          settled = true;
          clearTimeout(timeoutId);
          reject(...args);
        }
      }

      try {
        // First, try to get a session ID from the server
        let response;
        try {
          // Use the explicit IPv4 URL
          response = await fetch(`${this.apiBaseUrl}/api/live/session/start`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (!response.ok) {
            throw new Error(`Failed to start session: ${response.statusText}`);
          }

          const data = await response.json();
          this.sessionId = data.session_id;
          console.log(`Session started with ID: ${this.sessionId}`);
        } catch (err) {
          console.error('Error starting session:', err);

          // If server is unavailable, switch to mock mode
          if (err.message.includes('Failed to fetch') ||
            err.message.includes('NetworkError') ||
            err.message.includes('Failed to start session')) {
            console.warn('Server unavailable, switching to mock mode');
            this.mockMode = true;
            this.sessionId = 'mock-session-' + Date.now();

            // Simulate successful connection
            setTimeout(() => {
              this.isConnecting = false;
              if (onConnect) onConnect();
              safeResolve();
            }, 500);

            return;
          } else {
            safeReject(err);
            return;
          }
        }

        let wsBase = this.apiBaseUrl.replace(/^http(s?):/, 'ws$1:');

        // Always ensure /api prefix is added once
        const wsUrl = `${wsBase.replace(/\/$/, '')}/api/live/ws/${this.sessionId}`;

        // Log the WebSocket URL including the port
        try {
          const urlObj = new URL(wsUrl);
          console.log(`Connecting to WebSocket at ${urlObj.protocol}//${urlObj.hostname}:${urlObj.port}${urlObj.pathname}`);
        } catch (e) {
          console.warn('Could not parse WebSocket URL:', wsUrl);
        }

        this.ws = new WebSocket(wsUrl);

        // Add a timeout to avoid unresolved promise
        timeoutId = setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            safeReject(new Error('WebSocket connection timed out'));
          }
        }, 10000); // 10 seconds

        this.ws.onopen = () => {
          clearTimeout(timeoutId);
          console.log('WebSocket connection established');
          this.isConnecting = false;
          this.reconnectAttempts = 1;
          if (onConnect) onConnect();
          safeResolve(); // <-- resolves the promise when connected
        };

        this.ws.onclose = (event) => {
          clearTimeout(timeoutId);
          console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
          if (event.code !== 1000) {
            console.warn('WebSocket closed abnormally. Check backend/ngrok logs for details.');
          }
          this.ws = null;

          if (onDisconnect) onDisconnect();

          // Attempt to reconnect if not intentionally closed
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
            this.reconnectAttempts++;
            setTimeout(() => this.connect(onConnect, onDisconnect), 2000);
          }

          // Only reject if not reconnecting
          if (event.code !== 1000 && this.reconnectAttempts >= this.maxReconnectAttempts) {
            safeReject(new Error('WebSocket closed abnormally and max reconnects reached'));
          }
        };

        this.ws.onerror = (error) => {
          clearTimeout(timeoutId);
          console.error('WebSocket error:', error);
          this.isConnecting = false; // <-- Ensure flag is reset
          safeReject(error); // <-- rejects the promise on error
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            console.log(`Received message of type: ${message.type}`);

            if (this.handlers.has(message.type)) {
              this.handlers.get(message.type)(message.data);
            } else {
              console.warn(`No handler registered for message type: ${message.type}`);
            }
          } catch (error) {
            console.error('Error processing message:', error);
          }
        };
      } catch (error) {
        clearTimeout(timeoutId);
        console.error('Error connecting to WebSocket:', error);
        this.isConnecting = false;
        safeReject(error); // <-- rejects the promise on error
      }
    });
  }

  registerHandler(type, handler) {
    this.handlers.set(type, handler);
  }

  send(type, data) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket is not connected, cannot send message');
      return;
    }

    try {
      this.ws.send(JSON.stringify({ type, data }));
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  sendMockVideoFrame(frameData) {
    if (this.mockMode) {
      console.log('Mock: Video frame sent');

      // Simulate feedback every 5 seconds
      if (!this._mockFeedbackInterval) {
        this._mockFeedbackInterval = setInterval(() => {
          if (this.handlers.has(WSMessageType.FEEDBACK)) {
            console.log('Sending mock feedback');
            this.handlers.get(WSMessageType.FEEDBACK)({
              emotion: "neutral",
              eye_contact: "yes",
              transcript: "Mock transcript data",
              gemini_feedback: {
                posture_feedback: "Stand straight with shoulders back.",
                expression_feedback: "Try to vary your expressions to engage your audience.",
                eye_contact_feedback: "Maintain consistent eye contact with the camera.",
                voice_feedback: "Speak clearly and project your voice.",
                overall_suggestion: "Practice speaking with more energy and expression."
              },
              timestamp: new Date().toISOString()
            });
          }
        }, 2000);
      }
    }
  }

  sendMockAudioChunk(audioData) {
    if (this.mockMode) {
      console.log('Mock: Audio chunk sent');
    }
  }

  sendVideoFrame(frameData) {
    if (this.mockMode) {
      this.sendMockVideoFrame(frameData);
      return;
    }

    if (!frameData.startsWith('data:image')) {
      console.error('Invalid frame data format');
      return;
    }
    this.send(WSMessageType.VIDEO_FRAME, frameData);
  }

  sendAudioChunk(audioData) {
    if (this.mockMode) {
      this.sendMockAudioChunk(audioData);
      return;
    }

    if (!audioData) {
      console.error('Invalid audio data');
      return;
    }
    this.send(WSMessageType.AUDIO_CHUNK, audioData);
  }

  sendPong() {
    console.log('Sending PONG message');
    this.send(WSMessageType.PONG, { timestamp: new Date().toISOString() });
  }

  async disconnect() {
    // Clear mock feedback interval if it exists
    if (this._mockFeedbackInterval) {
      clearInterval(this._mockFeedbackInterval);
      this._mockFeedbackInterval = null;
    }

    if (this.sessionId && !this.mockMode) {
      try {
        await fetch(`${this.apiBaseUrl}/api/live/session/${this.sessionId}/stop`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Error stopping session:', error);
      }
    }

    if (this.ws) {
      try {
        this.ws.onclose = null;
        this.ws.onerror = null;
        this.ws.onopen = null;
        this.ws.onmessage = null;
        this.ws.close();
      } catch (e) {
        console.warn('Error during WebSocket disconnect:', e);
      }
      this.ws = null;
    }

    this.isConnecting = false;
    this.sessionId = null;
    this.handlers.clear();
    this.mockMode = false;
  }
}

// Create a singleton instance
const wsService = new WebSocketService();
export default wsService;