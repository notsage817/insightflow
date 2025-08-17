from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class ModelProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class MessageRole(str, Enum):
    """Message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    """Chat message model"""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    file_attachment: Optional[str] = None

class Conversation(BaseModel):
    """Conversation model"""
    id: str
    title: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime
    model_provider: ModelProvider
    model_name: str

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    model_provider: ModelProvider
    model_name: str
    conversation_id: Optional[str] = None
    file_content: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    message: Message
    conversation_id: str

class ModelInfo(BaseModel):
    """Model information"""
    provider: ModelProvider
    name: str
    display_name: str
    description: Optional[str] = None

class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    content: str
    size: int
    type: str