from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict
import json
import cv2
import numpy as np
import base64
import uuid
from datetime import datetime
import asyncio
import logging
from src.backend.ws_manager.ws_manager import manager
from scripts.live_pipeline.live_analysis_pipeline import run_analysis_once
from scripts.live_pipeline.audio_analysis import transcribe_audio
import sounddevice as sd

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/live",
    tags=["live analysis"],
)

# Message types for WebSocket communication
class WSMessageType:
    VIDEO_FRAME = "video_frame"
    AUDIO_CHUNK = "audio_chunk"
    FEEDBACK = "feedback"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"

@router.post("/session/start")
async def start_session():
    """Initialize a new live analysis session"""
    try:
        session_id = str(uuid.uuid4())
        return {"session_id": session_id, "status": "initialized"}
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize session")

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        # Start ping-pong task
        ping_task = asyncio.create_task(keep_alive(websocket, session_id))
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == WSMessageType.VIDEO_FRAME:
                await handle_video_frame(session_id, data)
            elif message_type == WSMessageType.AUDIO_CHUNK:
                await handle_audio_chunk(session_id, data)
            elif message_type == WSMessageType.PONG:
                manager.update_session_data(session_id, {"last_ping": datetime.now()})
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_id}")
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(session_id)
    finally:
        ping_task.cancel()

async def handle_video_frame(session_id: str, data: dict):
    try:
        # Convert base64 image to cv2 format
        frame_bytes = base64.b64decode(data["frame"].split(",")[1])
        frame_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
        
        # Run analysis
        result = run_analysis_once(frame)
        
        # Update frame count
        session_data = manager.get_session_data(session_id)
        session_data["frame_count"] += 1
        
        # Send feedback
        await manager.send_feedback(session_id, {
            "type": WSMessageType.FEEDBACK,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error processing video frame: {e}")
        await manager.send_feedback(session_id, {
            "type": WSMessageType.ERROR,
            "error": str(e)
        })

async def handle_audio_chunk(session_id: str, data: dict):
    try:
        # Decode audio data
        audio_chunk = np.frombuffer(
            base64.b64decode(data["audio"]), 
            dtype=np.float32
        )
        
        # Add to session buffer
        session_data = manager.get_session_data(session_id)
        session_data["audio_buffer"].extend(audio_chunk)
        
        # Process audio if buffer is large enough
        if len(session_data["audio_buffer"]) >= SAMPLE_RATE * 3:  # Process every 3 seconds
            audio_data = np.array(session_data["audio_buffer"])
            transcript = transcribe_audio(audio_data)
            session_data["audio_buffer"] = []  # Clear buffer
            
            await manager.send_feedback(session_id, {
                "type": WSMessageType.FEEDBACK,
                "data": {"transcript": transcript}
            })
            
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        await manager.send_feedback(session_id, {
            "type": WSMessageType.ERROR,
            "error": str(e)
        })

async def keep_alive(websocket: WebSocket, session_id: str):
    """Send ping messages to keep the connection alive"""
    try:
        while True:
            await asyncio.sleep(30)  # Send ping every 30 seconds
            await websocket.send_json({"type": WSMessageType.PING})
            
            # Check last ping time
            session_data = manager.get_session_data(session_id)
            if (datetime.now() - session_data["last_ping"]).seconds > 40:
                logger.warning(f"Session {session_id} timed out")
                await manager.disconnect(session_id)
                break
                
    except Exception as e:
        logger.error(f"Keep-alive error: {e}")
        await manager.disconnect(session_id)

@router.post("/session/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a live analysis session"""
    try:
        await manager.disconnect(session_id)
        return {"status": "stopped", "session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to stop session: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop session") 