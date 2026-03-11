from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://taskuser:supersecretpassword@localhost:5432/taskmaster"
)
# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_database():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
def wait_for_database(max_retries=30, delay=1):
    """Wait for database to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            # Try to create a connection
            connection = engine.connect()
            connection.close()
            logger.info("Database connection successful!")
            return True
        except Exception as e:
            retries += 1
            logger.warning(f"Database connection failed (attempt {retries}/{max_retries}): {e}")
            time.sleep(delay)
    
    logger.error("Could not connect to database after maximum retries")
    return False