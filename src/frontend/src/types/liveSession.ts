export interface LiveSessionState {
  status: 'idle' | 'recording' | 'stopped' | 'error';
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  feedback: {
    speech_rate: {
      wpm: number | null;
      assessment: string | null;
      suggestion: string | null;
    };
    filler_words: {
      total: number;
      counts: Record<string, number>;
      suggestion: string | null;
    };
    clarity: {
      score: number | null;
      suggestion: string | null;
    };
    sentiment: {
      label: string | null;
      score: number | null;
      suggestion: string | null;
    };
    keywords: {
      topics: string[];
      context: string | null;
    };
  } | null;
  sessionHistory: Array<{
    timestamp: Date;
    data: LiveSessionState['feedback'];
  }>;
}

export type LiveSessionAction =
  | { type: 'SET_STATUS'; payload: LiveSessionState['status'] }
  | { type: 'SET_CONNECTION'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SESSION_ID'; payload: string | null }
  | { type: 'UPDATE_FEEDBACK'; payload: Partial<NonNullable<LiveSessionState['feedback']>> }
  | { type: 'ADD_TO_HISTORY'; payload: { timestamp: Date; data: LiveSessionState['feedback'] } }
  | { type: 'RESET_SESSION' }; 