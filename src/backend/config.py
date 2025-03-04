from pydantic import BaseSettings

class Settings(BaseSettings):
    LLM_MODEL: str = "mistralai/Mistral-7B"
    UPLOAD_FOLDER: str = "uploads"

settings = Settings()