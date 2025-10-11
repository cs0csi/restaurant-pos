from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import time
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def get_database_connection(max_retries: int = 10, retry_delay: int = 2) -> Optional[create_engine]:
    """
    Attempt to connect to the database with retries
    """
    attempt = 0

    while attempt < max_retries:
        try:
            engine = create_engine(DB_URL)
            connection = engine.connect()
            connection.close()
            logger.info("Successfully connected to the database!")
            return engine
        except Exception as e:
            attempt += 1
            if attempt == max_retries:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                raise
            logger.warning(f"Database connection attempt {attempt} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

# Create engine with retry mechanism
engine = get_database_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODIFICATION: Added get_db dependency function here ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()