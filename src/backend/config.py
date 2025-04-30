# Modified on March 15 to load the Hugging Face API key
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the absolute path to the env file
env_path = Path(__file__).parent.parent.parent / ".env.development"
print(f"Looking for .env file at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")

# Load environment variables
load_dotenv(str(env_path))

# Debug: Print loaded environment variables
print("\nLoaded Environment Variables:")
print(f"HUGGINGFACE_API_KEY: {os.getenv('HUGGINGFACE_API_KEY')}")
print(f"MONGO_DB_URI: {os.getenv('MONGO_DB_URI')}")

class Settings(BaseSettings):
    # API Keys
    HUGGINGFACE_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    LLM_MODEL: str

    # Security
    SECRET_KEY: str
    AUTH_TOKEN_EXPIRE_MINUTES: str = "30"
    ALGORITHM: str = "HS256"

    # MongoDB Settings
    MONGO_DB_URI: str
    DB_CLOUD_PASSWORD: str
    DB_CLOUD_USERNAME: str

    # Upload Settings
    UPLOAD_FOLDER: str = "uploads"
    UPLOAD_DIR: str = "uploads/videos"

    # Transformer Config
    CUDA_LAUNCH_BLOCKING: str = "0"
    TOKENIZERS_PARALLELISM: str = "true"
    TORCH_USE_CUDA_DSA: str = "1"

    # Frontend Config
    REACT_APP_API_URL: str = "http://localhost:8000"
    VITE_API_UR: str | None = None


    # CORS Settings
    ALLOWED_HOSTS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "ws://localhost:8000",
        "https://your-ngrok-subdomain.ngrok-free.app",
    ]

    ALLOWED_HEADERS: list = [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ]

    ALLOWED_METHODS: list = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH"
    ]

    # WebSocket Settings
    WS_PING_INTERVAL: int = 30  # seconds
    WS_PING_TIMEOUT: int = 10   # seconds
    WS_MAX_MESSAGE_SIZE: int = 1024 * 1024  # 1MB

    class Config:
        env_file = str(env_path)
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "allow"

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
        except Exception as e:
            print(f"\nError initializing Settings: {str(e)}")
            print("Current environment variables:")
            for key in ["HUGGINGFACE_API_KEY", "MONGO_DB_URI", "UPLOAD_DIR"]:
                print(f"{key}: {os.getenv(key)}")
            raise

try:
    settings = Settings()
    print("\nSettings loaded successfully!")
except Exception as e:
    print(f"\nFailed to load settings: {str(e)}")
    raise
