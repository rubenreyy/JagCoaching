export const initialState = {
  status: 'idle',
  isConnected: false,
  isLoading: false,
  error: null,
  sessionId: null,
  feedback: null,
  sessionHistory: []
};

export function liveSessionReducer(state, action) {
  switch (action.type) {
    case 'SET_STATUS':
      return {
        ...state,
        status: action.payload
      };

    case 'SET_CONNECTION':
      return {
        ...state,
        isConnected: action.payload
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        status: action.payload ? 'error' : state.status
      };

    case 'SET_SESSION_ID':
      return {
        ...state,
        sessionId: action.payload
      };

    case 'UPDATE_FEEDBACK':
      return {
        ...state,
        feedback: {
          ...state.feedback,
          ...action.payload,
          speech_rate: {
            ...(state.feedback?.speech_rate || {}),
            ...(action.payload.speech_rate || {})
          },
          filler_words: {
            ...(state.feedback?.filler_words || { total: 0, counts: {} }),
            ...(action.payload.filler_words || {})
          },
          clarity: {
            ...(state.feedback?.clarity || {}),
            ...(action.payload.clarity || {})
          },
          sentiment: {
            ...(state.feedback?.sentiment || {}),
            ...(action.payload.sentiment || {})
          },
          keywords: {
            ...(state.feedback?.keywords || { topics: [] }),
            ...(action.payload.keywords || {})
          }
        }
      };

    case 'ADD_TO_HISTORY':
      return {
        ...state,
        sessionHistory: [...state.sessionHistory, action.payload]
      };

    case 'RESET_SESSION':
      return {
        ...initialState
      };

    default:
      return state;
  }
} 