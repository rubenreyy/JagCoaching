# Include the project root directory in the Python path if testing this file only
# third-party imports

import sys
import os
if sys.path.count(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) == 0:
    sys.path.append(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
from config import settings
from routers import auth_router , videos_router , users_router
import uvicorn
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

# Built-in imports
from contextlib import asynccontextmanager
from pathlib import Path


import dotenv

dotenv.load_dotenv("./env.development") # consolidated to one env folder

# dotenv.load_dotenv("./src/backend/.env.development")

# Local imports


UPLOAD_DIR = settings.UPLOAD_FOLDER


# Startup and shutdown event handlers for fastapi
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the upload directory on startup."""
    UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
    UPLOAD_DIR.mkdir(exist_ok=True)
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

# TODO: Include the routers in the main FastAPI application when database is working
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(videos_router)


# Added CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


    # allow_content_types=["application/json", "multipart/form-data", "application/x-www-form-urlencoded"],
# Index route


@app.get("/")
async def index():
    return {"message": "Welcome to the JagCoaching API!"}

# API route


@app.get("/api/", response_description="API index route")
async def apiroutes():
    """Returns information about all available API endpoints."""
    return {
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "This index page showing all available endpoints and welcome message."
            },
            {
                "path": "/api/upload/",
                "method": "POST",
                "description": "Upload a video file"
            },
            {
                "path": "/api/process-audio/",
                "method": "POST",
                "description": "Extract and analyze speech from an uploaded video"
            },
            {
                "path": "/api/login/",
                "method": "POST",
                "description": "Login to the application"
            },
            {
                "path": "/api/logout/",
                "method": "POST",
                "description": "Logout the user from the application"
            },
            {
                "path": "/api/register/",
                "method": "POST",
                "description": "Register a new user account"
            },
            {
                "path": "/api/user/",
                "method": "GET",
                "description": "Check if the user is logged in"
            },
            {
                "path": "/api/profile/",
                "method": "GET",
                "description": "Get profile data for the logged in user"
            },
        ],
        "version": "1.0"
    }





# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
