from enum import Enum

class WSMessageType(str, Enum):
    PING = "ping"
    PONG = "pong"
    VIDEO_FRAME = "video_frame"
    AUDIO_CHUNK = "audio_chunk"
    FEEDBACK = "feedback"
    ERROR = "error" 