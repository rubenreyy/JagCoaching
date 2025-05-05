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
    prefix="/live",
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
        logger.info(
            "WebSocket connection accepted for session %s",
            session_id,
        )

        # Initialize session data with metrics tracking
        session_data = {
            "last_ping": datetime.now(),
            "analysis_in_progress": False,
            "last_frame": None,
            "last_audio": None,
            "metrics": {
                "eye_contact": {
                    "yes": 0,
                    "limited": 0,
                    "total": 0,
                },
                "emotion": {
                    "happy": 0,
                    "neutral": 0,
                    "sad": 0,
                    "angry": 0,
                    "surprise": 0,
                    "total": 0,
                },
                "posture": {
                    "good": 0,
                    "poor": 0,
                    "total": 0,
                },
                "audio_quality": {
                    "excellent": 0,
                    "good": 0,
                    "moderate": 0,
                    "low": 0,
                    "none": 0,
                    "total": 0,
                },
            },
        }

        # Register connection with manager
        await manager.connect(session_id, websocket)

        # Start periodic feedback task
        feedback_task = asyncio.create_task(
            periodic_feedback(websocket, session_id, session_data)
        )

        # Helper function for message handling to reduce complexity
        async def handle_message(message, session_data):
            msg_type = message.get("type")
            if msg_type == WSMessageType.PING:
                await websocket.send_json({"type": WSMessageType.PONG})

            elif msg_type == WSMessageType.VIDEO_FRAME:
                # Log only once per second instead of every frame
                current_time = datetime.now()
                if (
                    not hasattr(websocket_endpoint, "last_frame_log")
                    or (
                        current_time
                        - websocket_endpoint.last_frame_log
                    ).total_seconds()
                    > 1
                ):
                    logger.debug(
                        "Received video frame from session %s",
                        session_id,
                    )
                    websocket_endpoint.last_frame_log = current_time

                # Store the frame for analysis
                session_data["last_frame"] = message["data"]

            elif msg_type == WSMessageType.AUDIO_CHUNK:
                logger.debug(
                    "Received audio chunk from session %s",
                    session_id,
                )
                session_data["last_audio"] = message["data"]

            else:
                logger.warning(
                    "Received unknown message type from session %s: %s",
                    session_id,
                    message.get("type"),
                )

        # Process incoming messages
        try:
            while True:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    websocket.receive_json(), timeout=30
                )

                # Update last ping time
                session_data["last_ping"] = datetime.now()

                # Process message based on type
                await handle_message(message, session_data)

        except WebSocketDisconnect:
            logger.info(
                "WebSocket disconnected for session %s",
                session_id,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "WebSocket timeout for session %s",
                session_id,
            )
        finally:
            # Cancel feedback task
            feedback_task.cancel()
            try:
                await feedback_task
            except asyncio.CancelledError:
                pass

            # Disconnect from manager
            await manager.disconnect(session_id)
            logger.info(
                "Session %s disconnected and cleanup complete",
                session_id,
            )

    except Exception as e:
        logger.error(
            "Error in WebSocket endpoint for session %s: %s",
            session_id,
            e,
            exc_info=True,
        )
        try:
            await manager.disconnect(session_id)
        except Exception:
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

# Update periodic feedback to track metrics
async def periodic_feedback(websocket: WebSocket, session_id: str, session_data: Dict):
    """Send periodic feedback based on latest frame and audio"""
    try:
        while True:
            # Wait for next feedback interval
            await asyncio.sleep(10)  # Send feedback every 10 seconds
            
            # Check if websocket is still connected
            if websocket.client_state == WebSocketState.DISCONNECTED:
                logger.info(f"WebSocket disconnected during periodic feedback for session {session_id}")
                break
            
            # Check if we have data to analyze
            try:
                has_frame = session_data["last_frame"] is not None
                has_audio = session_data["last_audio"] is not None
                
                # Only log once that we're generating feedback
                logger.info(f"Generating periodic feedback for session {session_id}")
                
                # Skip detailed logging about frame/audio presence
                
                # If analysis is already in progress, skip this round
                if session_data["analysis_in_progress"]:
                    logger.debug(f"Analysis already in progress for session {session_id}, skipping")
                    continue
                
                # Mark analysis as in progress
                session_data["analysis_in_progress"] = True
                
                # Check if we have a frame to analyze
                if has_frame:
                    # Get the frame data
                    frame = session_data["last_frame"]
                    audio_data = session_data["last_audio"]
                    
                    try:
                        # Run analysis with timeout
                        result = await asyncio.wait_for(
                            asyncio.to_thread(run_analysis_once, frame, audio_data),
                            timeout=5.0  # 5 second timeout
                        )
                        
                        # Update metrics with the result
                        if result:
                            metrics = session_data["metrics"]
                            
                            # Update eye contact metrics
                            if "eye_contact" in result:
                                eye_contact = result["eye_contact"]
                                metrics["eye_contact"]["total"] += 1
                                if eye_contact in metrics["eye_contact"]:
                                    metrics["eye_contact"][eye_contact] += 1
                            
                            # Update emotion metrics
                            if "emotion" in result:
                                emotion = result["emotion"]
                                metrics["emotion"]["total"] += 1
                                if emotion in metrics["emotion"]:
                                    metrics["emotion"][emotion] += 1
                            
                            # Update posture metrics
                            if "posture" in result:
                                posture = result["posture"]
                                metrics["posture"]["total"] += 1
                                if posture in metrics["posture"]:
                                    metrics["posture"][posture] += 1
                            
                            # Update audio quality metrics
                            if "audio_quality" in result:
                                audio_quality = result["audio_quality"]
                                metrics["audio_quality"]["total"] += 1
                                if audio_quality in metrics["audio_quality"]:
                                    metrics["audio_quality"][audio_quality] += 1
                        
                        # Send feedback to client
                        await websocket.send_json({
                            "type": WSMessageType.FEEDBACK,
                            "data": result
                        })
                        
                        logger.info(f"Sent feedback to session {session_id}")
                    except asyncio.TimeoutError:
                        logger.warning(f"Analysis timed out for session {session_id}")
                        await send_fallback_feedback(websocket, session_id, "Analysis is taking longer than expected")
                    except Exception as e:
                        logger.error(f"Error in analysis for session {session_id}: {e}")
                        await send_fallback_feedback(websocket, session_id, "Analysis encountered an error")
                    finally:
                        # Mark analysis as complete
                        session_data["analysis_in_progress"] = False
                else:
                    logger.warning(f"No frame data available for session {session_id}")
                    # Send placeholder feedback
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
                
            except Exception as e:
                logger.error(f"Error generating feedback for session {session_id}: {e}")
                try:
                    await send_fallback_feedback(websocket, session_id, "Error generating feedback")
                except:
                    pass
                
    except Exception as e:
        logger.error(f"Periodic feedback error for session {session_id}: {e}")

# Add a new endpoint to get session metrics
@router.get("/session/{session_id}/metrics")
async def get_session_metrics(session_id: str):
    """Get metrics for a session"""
    try:
        # Get session data from manager
        session_data = manager.get_session_data(session_id)
        if not session_data or "metrics" not in session_data:
            raise HTTPException(status_code=404, detail="Session metrics not found")
        
        return {"session_id": session_id, "metrics": session_data["metrics"]}
    except Exception as e:
        logger.error(f"Failed to get metrics for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get session metrics")

# Update stop_session to include metrics
@router.post("/session/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a live analysis session and return metrics"""
    try:
        logger.info(f"Stopping session {session_id}")
        
        # Get session metrics before disconnecting
        session_data = manager.get_session_data(session_id)
        metrics = session_data.get("metrics", {}) if session_data else {}
        
        # Disconnect the session
        await manager.disconnect(session_id)
        
        return {
            "status": "stopped", 
            "session_id": session_id,
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Failed to stop session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stop session") 