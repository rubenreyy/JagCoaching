export enum WSMessageType {
  VIDEO_FRAME = "video_frame",
  AUDIO_CHUNK = "audio_chunk",
  FEEDBACK = "feedback",
  ERROR = "error",
  PING = "ping",
  PONG = "pong"
}

export interface WSMessage {
  type: WSMessageType;
  data?: any;
  error?: string;
}

export interface FeedbackData {
  emotion: string;
  eye_contact: string;
  transcript: string;
  gemini_feedback: any;
  timestamp: string;
}

export interface SessionStatus {
  isConnected: boolean;
  isRecording: boolean;
  error: string | null;
  sessionId: string | null;
} 