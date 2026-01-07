from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.core import security
from app.db import models
from app.schemas import chat as chat_schemas
from app.routers import deps
from app.services.chat_service import chat_service
from app.services import file_service
from app.services.web_service import web_service
from fastapi import UploadFile, File
from datetime import datetime

router = APIRouter()

async def generate_title_background(session_id: int, content: str):
    db = deps.database.SessionLocal()
    try:
        # Check if title is still default
        session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
        if not session or session.title != "New Chat":
            return

        prompt = f"Summarize the following user input into a short, concise title (max 5 words). Do not use quotes. Input: {content[:200]}"
        
        # We need to collect the response from the stream
        generator = chat_service.chat_completion_stream([{"role": "user", "content": prompt}], model="qwen-plus")
        title = ""
        async for chunk in generator:
            title += chunk
            
        title = title.strip().strip('"').strip("'")
        if title:
            session.title = title
            db.commit()
    except Exception as e:
        print(f"Error auto-generating title: {e}")
    finally:
        db.close()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(deps.get_current_user)):
    content = await file.read()
    result = await file_service.process_file(content, file.filename)
    return {"filename": file.filename, "result": result}


@router.post("/sessions", response_model=chat_schemas.ChatSession)
def create_session(session: chat_schemas.ChatSessionCreate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    db_session = models.ChatSession(**session.dict(), user_id=current_user.id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[chat_schemas.ChatSession])
def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == current_user.id).order_by(models.ChatSession.updated_at.desc()).offset(skip).limit(limit).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=chat_schemas.ChatSession)
def get_session(session_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.patch("/sessions/{session_id}", response_model=chat_schemas.ChatSession)
def update_session(session_id: int, session_update: chat_schemas.ChatSessionUpdate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_session.title = session_update.title
    db.commit()
    db.refresh(db_session)
    return db_session

@router.post("/sessions/{session_id}/summary", response_model=chat_schemas.ChatSession)
async def generate_session_summary(session_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Get first few messages
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at).limit(4).all()
    if not messages:
        return db_session
        
    conversation = "\n".join([f"{msg.role}: {msg.content[:200]}" for msg in messages]) # Limit content
    prompt = f"Summarize the following conversation into a short title (max 5 words):\n\n{conversation}"
    
    try:
        # Use a default model for summary
        # Note: chat_completion_stream returns a generator, we need to iterate
        generator = chat_service.chat_completion_stream([{"role": "user", "content": prompt}], model="qwen-plus")
        title = ""
        async for chunk in generator:
            title += chunk
            
        title = title.strip().strip('"').strip("'")
        if title:
            db_session.title = title
            db.commit()
            db.refresh(db_session)
    except Exception as e:
        print(f"Error generating summary: {e}")
        
    return db_session

@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: int, message: chat_schemas.ChatMessageCreate, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Construct the actual text content that includes context
    actual_text_content = message.content
    
    # Check for URLs and fetch content
    urls = web_service.extract_urls(message.content)
    if urls:
        web_context = "\n\n--- Web Search Results ---\n"
        for url in urls:
            content = await web_service.fetch_content(url)
            web_context += content + "\n---\n"
        actual_text_content += web_context

    if message.file_context:
        actual_text_content = f"Reference Document Content:\n---\n{message.file_context}\n---\n\nUser Question: {actual_text_content}"

    # Auto-generate title if needed
    if session.title == "New Chat":
        # Check if this is the first few messages
        msg_count = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).count()
        if msg_count == 0: # This is the first message (we haven't added it yet? No, we add it below. Wait.)
             # Logic: We add message below. So count will be 1 after commit.
             # But here count is 0. So yes, this is the first message.
             background_tasks.add_task(generate_title_background, session_id, message.content) # Use original content for title, not the full context prompt

    # Update session timestamp
    session.updated_at = datetime.utcnow()
    db.add(session)

    # Save user message
    stored_content = actual_text_content
    if message.images:
        for idx, img in enumerate(message.images):
            # If the image is very long (base64), we might not want to store the whole thing in the text content for display history if we parse it differently later. 
            # But for now, let's keep it consistent.
            stored_content += f"\n\n![Image {idx+1}]({img})"

    user_msg = models.ChatMessage(session_id=session_id, role="user", content=stored_content, model=message.model)
    db.add(user_msg)
    db.commit()

    # Prepare context
    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at).all()
    
    messages = []
    for i, msg in enumerate(history):
        # Check if this is the message we just added (the last one) and if it has an image
        if i == len(history) - 1 and message.images and msg.id == user_msg.id:
             content_list = [{"type": "text", "text": actual_text_content}]
             for img in message.images:
                 content_list.append({"type": "image_url", "image_url": {"url": img}})
             
             messages.append({
                 "role": "user",
                 "content": content_list
             })
        else:
             messages.append({"role": msg.role, "content": msg.content})

    async def stream_generator():
        full_response = ""
        async for chunk in chat_service.chat_completion_stream(messages, model=message.model):
            full_response += chunk
            yield chunk
        
        try:
            # We need a new session because the request session might be closed or not thread safe in async generator
            new_db = deps.database.SessionLocal()
            assistant_msg = models.ChatMessage(session_id=session_id, role="assistant", content=full_response, model=message.model)
            new_db.add(assistant_msg)
            new_db.commit()
            new_db.close()
        except Exception as e:
            print(f"Error saving message: {e}")

    return StreamingResponse(stream_generator(), media_type="text/plain")
