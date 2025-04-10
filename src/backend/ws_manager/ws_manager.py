from fastapi import WebSocket
from typing import Dict, Set
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, dict] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, initial_data: dict = None):
        """Connect a new client and initialize its session data"""
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = initial_data or {}
        logger.info(f"Client connected to session {session_id}")

    def update_session_data(self, session_id: str, data: dict):
        """Update session data with new values"""
        if session_id in self.session_data:
            self.session_data[session_id].update(data)
            
    def get_session_data(self, session_id: str) -> dict:
        """Get session data, creating empty dict if needed"""
        return self.session_data.get(session_id, {})

    async def disconnect(self, session_id: str):
        """Disconnect a client and clean up its data"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket for session {session_id}: {e}")
            finally:
                del self.active_connections[session_id]
                self.session_data.pop(session_id, None)
                logger.info(f"Client disconnected from session {session_id}")

    async def send_feedback(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending feedback to session {session_id}: {e}")
                await self.disconnect(session_id)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

# Create global instance
manager = ConnectionManager() 