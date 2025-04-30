import { createContext, useContext, useReducer, useCallback } from 'react';
import { liveSessionReducer, initialState } from '../reducers/liveSessionReducer';

const LiveSessionContext = createContext(null);

export function LiveSessionProvider({ children }) {
  const [state, dispatch] = useReducer(liveSessionReducer, initialState);

  const actions = {
    setStatus: useCallback((status) => {
      dispatch({ type: 'SET_STATUS', payload: status });
    }, []),

    setConnection: useCallback((isConnected) => {
      dispatch({ type: 'SET_CONNECTION', payload: isConnected });
    }, []),

    setLoading: useCallback((isLoading) => {
      dispatch({ type: 'SET_LOADING', payload: isLoading });
    }, []),

    setError: useCallback((error) => {
      dispatch({ type: 'SET_ERROR', payload: error });
    }, []),

    setSessionId: useCallback((sessionId) => {
      dispatch({ type: 'SET_SESSION_ID', payload: sessionId });
    }, []),

    updateFeedback: useCallback((feedback) => {
      dispatch({ type: 'UPDATE_FEEDBACK', payload: feedback });
      dispatch({
        type: 'ADD_TO_HISTORY',
        payload: { timestamp: new Date(), data: feedback }
      });
    }, []),

    resetSession: useCallback(() => {
      dispatch({ type: 'RESET_SESSION' });
    }, [])
  };

  // Add session persistence
  const persistSession = useCallback(async () => {
    if (!state.sessionId || !state.feedback) return;
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: state.sessionId,
          feedback: state.feedback,
          history: state.sessionHistory
        })
      });
      
      if (!response.ok) throw new Error('Failed to save session');
      return response.json();
    } catch (error) {
      actions.setError(`Failed to persist session: ${error.message}`);
      throw error;
    }
  }, [state.sessionId, state.feedback, state.sessionHistory]);

  return (
    <LiveSessionContext.Provider value={{ state, actions, persistSession }}>
      {children}
    </LiveSessionContext.Provider>
  );
}

export function useLiveSession() {
  const context = useContext(LiveSessionContext);
  if (!context) {
    throw new Error('useLiveSession must be used within a LiveSessionProvider');
  }
  return context;
} 