
import logging

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_database
from sqlalchemy import text
from datetime import datetime

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check(db: Session = Depends(get_database)):
    """Health check endpoint that tests database connection"""
    try:
        # Simple query to test connection
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")