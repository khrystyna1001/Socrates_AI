from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import logging
from typing import Optional
from uuid import UUID

from ..database import get_database, wait_for_database, engine
from ..models.auth import Base, User, Task, Priority, Status

router = APIRouter()

logger = logging.getLogger(__name__)

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = None
class UserLogin(BaseModel):
    username: str
    password: str
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    due_date: Optional[datetime] = None
class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    priority: Priority
    status: Status
    created_at: datetime
    due_date: Optional[datetime] = None
    class Config:
        from_attributes = True

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
@router.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting TaskMaster API...")
    if not wait_for_database():
        raise Exception("Could not connect to database")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

@router.get("/")
async def root():
    return {"message": "Welcome to TaskMaster API! 🚀", "status": "operational"}

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_database)):
    """Register a new user"""
    # Check if user exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User registered successfully", "user_id": str(db_user.id)}

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_database)):
    """Login user and return JWT token"""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create a new task"""
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        owner_id=current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
    status_filter: Status = None,
    priority_filter: Priority = None
):
    """Get user's tasks with optional filtering"""
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return tasks
    
@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    new_status: Status,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update task status"""
    task = db.query(Task).filter(
        Task.id == task_id, 
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Task status updated successfully"}
