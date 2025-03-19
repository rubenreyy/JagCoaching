from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a SQLAlchemy session
    
    This should be used with FastAPI's Depends to inject the database session
    into route functions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize the database by creating all tables
    
    Call this function when starting the application to ensure all models
    are created in the database.
    """
    Base.metadata.create_all(bind=engine)