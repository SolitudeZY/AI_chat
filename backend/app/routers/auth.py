from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db import models
from app.schemas import user as user_schemas
from app.routers import deps
import shutil
import os
import uuid

router = APIRouter()

@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=user_schemas.User)
def register_user(user: user_schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=user_schemas.User)
async def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.put("/me", response_model=user_schemas.User)
async def update_user_me(user_update: user_schemas.UserUpdate, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    if user_update.password:
        current_user.hashed_password = security.get_password_hash(user_update.password)
    if user_update.email:
        current_user.email = user_update.email
    if user_update.username:
        current_user.username = user_update.username
    if user_update.avatar_url:
        current_user.avatar_url = user_update.avatar_url
    if user_update.bio:
        current_user.bio = user_update.bio
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/avatar", response_model=user_schemas.User)
async def upload_avatar(file: UploadFile = File(...), current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"uploads/{filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update user avatar_url
    # Assuming the server is running on localhost:8000. In production this should be configured.
    avatar_url = f"http://localhost:8000/uploads/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user
