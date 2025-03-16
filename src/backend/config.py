# Modified on March 15 to load the Hugging Face API key
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY")
    # LLM_MODEL: str = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-v0.1")  # Default model
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai-community/gpt2")  # Default model
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")

settings = Settings()
