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
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "start_time": datetime.now(),
            "last_ping": datetime.now(),
            "audio_buffer": [],
            "frame_count": 0
        }
        logger.info(f"Client connected to session {session_id}")

    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].close()
            del self.active_connections[session_id]
            del self.session_data[session_id]
            logger.info(f"Client disconnected from session {session_id}")

    async def send_feedback(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

    def get_session_data(self, session_id: str) -> dict:
        return self.session_data.get(session_id, {})

    def update_session_data(self, session_id: str, data: dict):
        if session_id in self.session_data:
            self.session_data[session_id].update(data)

# Create global instance
manager = ConnectionManager() 