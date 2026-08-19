# Main FastAPI Application File
# This file serves as the entry point for the FastAPI demo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from app.routers import users, items

# Import database initialization
from app.database import engine, Base
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI application...")
    yield
    # Shutdown
    print("Shutting down FastAPI application...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A simple FastAPI demo application",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/", tags=["root"])
async def read_root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI Demo!", "version": "1.0.0"}

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

# ============================================================================
# FOLDER STRUCTURE AND FILES TO CREATE
# ============================================================================
# 
# fastapi_demo/
# ├── main.py (this file)
# ├── requirements.txt
# ├── .env
# └── app/
#     ├── __init__.py
#     ├── config.py
#     ├── database.py
#     ├── dependencies.py
#     ├── models/
#     │   ├── __init__.py
#     │   ├── user.py
#     │   └── item.py
#     ├── schemas/
#     │   ├── __init__.py
#     │   ├── user.py
#     │   └── item.py
#     ├── services/
#     │   ├── __init__.py
#     │   ├── user_service.py
#     │   └── item_service.py
#     └── routers/
#         ├── __init__.py
#         ├── users.py
#         └── items.py
#
# ============================================================================
# FILE CONTENTS
# ============================================================================

# ============ app/config.py ============
"""
Configuration settings for the FastAPI application
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "FastAPI Demo"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./test.db"
    # For PostgreSQL: "postgresql://user:password@localhost/dbname"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# ============ app/database.py ============
"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ app/dependencies.py ============
"""
Shared dependencies for route handlers
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_user(db: Session = Depends(get_db)):
    """Dependency to get current user (placeholder)"""
    return {"user_id": 1, "username": "demo_user"}

def verify_token(token: str = None):
    """Dependency to verify authentication token"""
    if not token:
        return None
    return {"token": token}

# ============ app/models/user.py ============
"""
SQLAlchemy ORM models for User
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ============ app/models/item.py ============
"""
SQLAlchemy ORM models for Item
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(500))
    price = Column(Float)
    owner_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ============ app/schemas/user.py ============
"""
Pydantic schemas for User request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ app/schemas/item.py ============
"""
Pydantic schemas for Item request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ app/services/user_service.py ============
"""
Business logic for User operations
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user: UserUpdate):
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
        return db_user

# ============ app/services/item_service.py ============
"""
Business logic for Item operations
"""
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    @staticmethod
    def create_item(db: Session, item: ItemCreate, owner_id: int):
        db_item = Item(**item.model_dump(), owner_id=owner_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_item(db: Session, item_id: int):
        return db.query(Item).filter(Item.id == item_id).first()
    
    @staticmethod
    def get_all_items(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Item).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_item(db: Session, item_id: int, item: ItemUpdate):
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if db_item:
            update_data = item.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)
            db.commit()
            db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete_item(db: Session, item_id: int):
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item

# ============ app/routers/users.py ============
"""
Route handlers for User endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = UserService.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return UserService.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = UserService.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    return UserService.get_all_users(db, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    db_user = UserService.update_user(db, user_id=user_id, user=user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    db_user = UserService.delete_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# ============ app/routers/items.py ============
"""
Route handlers for Item endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter()

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new item"""
    return ItemService.create_item(db=db, item=item, owner_id=current_user["user_id"])

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID"""
    db_item = ItemService.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.get("/", response_model=list[ItemResponse])
def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all items"""
    return ItemService.get_all_items(db, skip=skip, limit=limit)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update item"""
    db_item = ItemService.update_item(db, item_id=item_id, item=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete item"""
    db_item = ItemService.delete_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# ============ requirements.txt ============
"""
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.6.0
pydantic-settings==2.1.0
pydantic[email]==2.6.0
python-dotenv==1.0.0
"""
