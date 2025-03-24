# Modified on March 15 to load the Hugging Face API key
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("./.env.development")

class Settings(BaseSettings):
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY")
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    ALLOWED_HOSTS: list = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HEADERS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]

settings = Settings()
