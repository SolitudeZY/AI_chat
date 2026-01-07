from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    role: Optional[str] = "user"
    model: Optional[str] = "qwen-plus" # Default model
    images: Optional[List[str]] = [] # List of Base64 or URL
    file_context: Optional[str] = None # Extracted text from file

class ChatMessage(ChatMessageBase):
    id: int
    role: str
    session_id: int
    created_at: datetime
    model: Optional[str] = None

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: str

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True
