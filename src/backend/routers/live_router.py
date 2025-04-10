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
from starlette.websockets import WebSocketState
import concurrent.futures

logger = logging.getLogger(__name__)

# Create a thread pool for running analysis
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

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
        logger.info(f"Starting new session with ID: {session_id}")
        return {"session_id": session_id, "status": "initialized"}
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize session")

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live analysis"""
    try:
        # Accept the connection first
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for session {session_id}")
        
        # Initialize session data
        session_data = {
            "last_ping": datetime.now(),
            "analysis_in_progress": False,
            "last_frame": None,
            "last_audio": None
        }
        
        # Then connect to manager with initialized data
        await manager.connect(websocket, session_id, session_data)
        
        # Send initial feedback
        await send_initial_feedback(websocket, session_id)
        
        # Start periodic feedback task
        feedback_task = asyncio.create_task(send_periodic_feedback(websocket, session_id))
        
        try:
            while True:
                try:
                    data = await websocket.receive_json()
                    message_type = data.get("type")
                    message_data = data.get("data")
                    
                    logger.info(f"Received {message_type} message from session {session_id}")
                    
                    if message_type == WSMessageType.VIDEO_FRAME:
                        # Log receipt of frame
                        logger.info(f"Received video frame from session {session_id}, data length: {len(message_data) if message_data else 0}")
                        manager.update_session_data(session_id, {"last_frame": message_data})
                        
                    elif message_type == WSMessageType.AUDIO_CHUNK:
                        # Log receipt of audio
                        logger.info(f"Received audio chunk from session {session_id}, data length: {len(message_data) if message_data else 0}")
                        manager.update_session_data(session_id, {"last_audio": message_data})
                        
                    elif message_type == WSMessageType.PONG:
                        manager.update_session_data(session_id, {"last_ping": datetime.now()})
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from client")
                    continue
                    
        except WebSocketDisconnect:
            logger.info(f"Client disconnected from session {session_id}")
        finally:
            feedback_task.cancel()
            await manager.disconnect(session_id)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.disconnect(session_id)
        except:
            pass

# ADDED: New function to send initial feedback
async def send_initial_feedback(websocket, session_id):
    """Send initial feedback immediately after connection"""
    try:
        await websocket.send_json({
            "type": WSMessageType.FEEDBACK,
            "data": {
                "timestamp": datetime.now().isoformat(),
                "emotion": "neutral",
                "eye_contact": "yes",
                "transcript": "Waiting for speech...",
                "gemini_feedback": {
                    "posture_feedback": "Stand straight with shoulders back.",
                    "expression_feedback": "Add more expression to engage your audience.",
                    "eye_contact_feedback": "Look directly at the camera.",
                    "voice_feedback": "Speak clearly and project your voice.",
                    "overall_suggestion": "Continue practicing with more energy and expression."
                }
            }
        })
        logger.info(f"Sent initial feedback to session {session_id}")
    except Exception as e:
        logger.error(f"Error sending initial feedback for session {session_id}: {e}")

# ADDED: New function to send dummy feedback
async def send_dummy_feedback(websocket, session_id):
    """Send dummy feedback for testing"""
    try:
        await websocket.send_json({
            "type": WSMessageType.FEEDBACK,
            "data": {
                "timestamp": datetime.now().isoformat(),
                "emotion": "neutral",
                "eye_contact": "yes",
                "transcript": "This is a test transcript.",
                "gemini_feedback": {
                    "posture_feedback": "Your posture appears good. Keep your back straight and shoulders relaxed.",
                    "expression_feedback": "Your facial expression is neutral. Try to vary your expressions to engage your audience.",
                    "eye_contact_feedback": "You're maintaining good eye contact. Continue looking directly at the camera.",
                    "voice_feedback": "Your speech is clear. Try to vary your tone for emphasis.",
                    "overall_suggestion": "You're doing well! Continue practicing with varied expressions and speech patterns."
                }
            }
        })
        logger.info(f"Sent dummy feedback to session {session_id}")
    except Exception as e:
        logger.error(f"Error sending dummy feedback for session {session_id}: {e}")

async def send_fallback_feedback(websocket, session_id, error_message):
    """Send fallback feedback when analysis fails"""
    try:
        await websocket.send_json({
            "type": WSMessageType.FEEDBACK,
            "data": {
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
                "gemini_feedback": {
                    "posture_feedback": "Analysis in progress...",
                    "expression_feedback": "Analysis in progress...",
                    "eye_contact_feedback": "Analysis in progress...",
                    "voice_feedback": "Analysis in progress...",
                    "overall_suggestion": "Please continue speaking naturally."
                }
            }
        })
        logger.info(f"Sent fallback feedback to session {session_id}")
    except Exception as e:
        logger.error(f"Error sending fallback feedback for session {session_id}: {e}")

async def keep_alive(websocket: WebSocket, session_id: str):
    """Send ping messages to keep the connection alive"""
    try:
        while True:
            await asyncio.sleep(30)  # Send ping every 30 seconds
            
            # Check if session still exists
            if session_id not in manager.active_connections:
                logger.info(f"Session {session_id} no longer active, stopping keep-alive")
                break
                
            # Check if websocket is still open
            if websocket.client_state == WebSocketState.DISCONNECTED:
                logger.info(f"WebSocket for session {session_id} disconnected, stopping keep-alive")
                break
                
            logger.debug(f"Sending PING to session {session_id}")
            try:
                await websocket.send_json({"type": WSMessageType.PING})
                
                # Check last ping time
                session_data = manager.get_session_data(session_id)
                if session_data and "last_ping" in session_data:
                    if (datetime.now() - session_data["last_ping"]).seconds > 40:
                        logger.warning(f"Session {session_id} timed out")
                        await manager.disconnect(session_id)
                        break
            except Exception as e:
                logger.error(f"Error sending ping for session {session_id}: {e}")
                break
                
    except Exception as e:
        logger.error(f"Keep-alive error for session {session_id}: {e}", exc_info=True)
        try:
            await manager.disconnect(session_id)
        except:
            pass

# Add this new function after the keep_alive function
async def send_periodic_feedback(websocket: WebSocket, session_id: str):
    """Send periodic feedback to the client"""
    try:
        while True:
            await asyncio.sleep(10)  # Send feedback every 10 seconds
            
            try:
                # Check if websocket is still connected
                if websocket.client_state != WebSocketState.CONNECTED:
                    logger.info(f"WebSocket for session {session_id} is no longer connected, stopping periodic feedback")
                    break
                
                # Get session data
                session_data = manager.get_session_data(session_id)
                
                # Skip if analysis is already in progress
                if session_data.get("analysis_in_progress", False):
                    logger.debug(f"Analysis already in progress for session {session_id}, skipping periodic feedback")
                    continue
                
                # Get the latest frame and audio data
                frame = session_data.get("last_frame")
                audio_data = session_data.get("last_audio")
                
                # Log what data we have
                logger.info(f"Periodic feedback for session {session_id}: " +
                           f"has frame: {frame is not None}, " +
                           f"has audio: {audio_data is not None}")
                
                # If we have at least one type of data, proceed with analysis
                if frame is not None or audio_data is not None:
                    # Mark analysis as in progress
                    session_data["analysis_in_progress"] = True
                    
                    try:
                        # Run analysis with available data
                        result = await asyncio.wait_for(
                            asyncio.to_thread(run_analysis_once, frame, audio_data),
                            timeout=5.0  # 5 second timeout
                        )
                        
                        # Send feedback to client
                        await websocket.send_json({
                            "type": WSMessageType.FEEDBACK,
                            "data": result
                        })
                        
                        logger.info(f"Sent periodic feedback to session {session_id}")
                    except asyncio.TimeoutError:
                        logger.warning(f"Periodic analysis timed out for session {session_id}")
                        await send_fallback_feedback(websocket, session_id, "Analysis is taking longer than expected")
                    except Exception as e:
                        logger.error(f"Error in periodic analysis for session {session_id}: {e}", exc_info=True)
                        await send_fallback_feedback(websocket, session_id, "Analysis encountered an error")
                    finally:
                        # Mark analysis as complete
                        session_data["analysis_in_progress"] = False
                else:
                    logger.warning(f"No frame or audio data available for session {session_id}, sending placeholder feedback")
                    # Send placeholder feedback similar to test output
                    await websocket.send_json({
                        "type": WSMessageType.FEEDBACK,
                        "data": {
                            "timestamp": datetime.now().isoformat(),
                            "emotion": "neutral",
                            "eye_contact": "yes",
                            "transcript": "No speech detected",
                            "gemini_feedback": {
                                "posture_feedback": "Stand straight with shoulders back.",
                                "expression_feedback": "Try to vary your expressions to engage your audience.",
                                "eye_contact_feedback": "Maintain consistent eye contact with the camera.",
                                "voice_feedback": "Speak clearly and project your voice.",
                                "overall_suggestion": "Practice speaking with more energy and expression."
                            }
                        }
                    })
                    logger.info(f"Sent placeholder feedback to session {session_id}")
                
            except Exception as e:
                logger.error(f"Error generating periodic feedback for session {session_id}: {e}", exc_info=True)
                try:
                    await send_fallback_feedback(websocket, session_id, "Error generating feedback")
                except:
                    pass
                
    except Exception as e:
        logger.error(f"Periodic feedback error for session {session_id}: {e}", exc_info=True)

@router.post("/session/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a live analysis session"""
    try:
        logger.info(f"Stopping session {session_id}")
        await manager.disconnect(session_id)
        return {"status": "stopped", "session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to stop session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stop session") 