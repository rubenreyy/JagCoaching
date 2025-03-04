from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    status: str

class SpeechEvaluationRequest(BaseModel):
    transcript: str

class SpeechEvaluationResponse(BaseModel):
    feedback: str
