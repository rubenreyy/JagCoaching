from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    status: str

class SpeechEvaluationRequest(BaseModel):
    transcript: str

class SpeechEvaluationResponse(BaseModel):
    feedback: str

class User(BaseModel):
    username: str
    email: str
    full_name: str = None
    disabled: bool = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

