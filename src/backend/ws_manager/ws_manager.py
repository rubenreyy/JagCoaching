"""
WebSocket connection and session management for JagCoaching backend.

This module provides classes to manage WebSocket connections and per-session data
for real-time feedback and communication between the backend and clients.
It supports connecting/disconnecting clients, sending feedback, broadcasting messages,
and storing/retrieving session-specific data.

Classes:
    ConnectionManager: Handles WebSocket connections and session data for each client.
    WebSocketManager: Alternative manager for WebSocket connections and session data.

Usage:
    - Use the global `manager` instance of ConnectionManager for managing connections.
    - Each session is identified by a unique session_id.
    - Session data can be updated and retrieved for each connection.
"""

from fastapi import WebSocket
from typing import Dict, Set
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections and session data for each client session.

    Methods:
        connect(websocket, session_id, initial_data): Register a new connection and initialize session data.
        update_session_data(session_id, data): Update session data for a session.
        get_session_data(session_id): Retrieve session data for a session.
        disconnect(session_id): Disconnect a client and clean up its data.
        send_feedback(session_id, message): Send a feedback message to a specific client.
        broadcast(message): Send a message to all connected clients.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str, initial_data: dict = None):
        """Connect a new client and initialize its session data."""
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = initial_data or {}
        logger.info(f"Client connected to session {session_id}")

    def update_session_data(self, session_id: str, data: dict):
        """Update session data with new values."""
        if session_id in self.session_data:
            self.session_data[session_id].update(data)

    def get_session_data(self, session_id: str) -> dict:
        """Get session data, creating empty dict if needed."""
        return self.session_data.get(session_id, {})

    async def disconnect(self, session_id: str):
        """Disconnect a client and clean up its data."""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.close()
            except Exception as e:
                logger.error(
                    f"Error closing WebSocket for session {session_id}: {e}")
            finally:
                del self.active_connections[session_id]
                self.session_data.pop(session_id, None)
                logger.info(f"Client disconnected from session {session_id}")

    async def send_feedback(self, session_id: str, message: dict):
        """Send a feedback message to a specific client session."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(
                    f"Error sending feedback to session {session_id}: {e}")
                await self.disconnect(session_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected_sessions = []
        for session_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(
                    f"Error broadcasting to session {session_id}: {e}")
                disconnected_sessions.append(session_id)
        # Clean up any connections that failed
        for session_id in disconnected_sessions:
            await self.disconnect(session_id)


# Create global instance for use throughout the backend
manager = ConnectionManager()

# Add session data storage to WebSocketManager


class WebSocketManager:
    """
    Alternative WebSocket manager for handling connections and session data.

    Methods:
        connect(session_id, websocket): Register a new connection.
        disconnect(session_id): Remove a connection (session data is retained).
        get_session_data(session_id): Retrieve session data for a session.
        update_session_data(session_id, data): Update session data for a session.
        send_message(session_id, message): Send a message to a specific client.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, Dict] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Register a new connection and initialize session data if needed."""
        self.active_connections[session_id] = websocket
        # Initialize session data if not exists
        if session_id not in self.session_data:
            self.session_data[session_id] = {}

    async def disconnect(self, session_id: str):
        """Remove a connection; session data is retained for later retrieval."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        # Keep session data for potential retrieval after disconnect

    def get_session_data(self, session_id: str) -> Dict:
        """Retrieve session data for a session."""
        return self.session_data.get(session_id, {})

    def update_session_data(self, session_id: str, data: Dict):
        """Update session data for a session."""
        if session_id in self.session_data:
            self.session_data[session_id].update(data)
        else:
            self.session_data[session_id] = data

    async def send_message(self, session_id: str, message: Dict):
        """Send a message to a specific client session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
