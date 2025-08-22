import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from models.chat import (
    ChatRequest, ChatResponse, Conversation, Message, MessageRole, 
    ModelProvider, ModelInfo, FileUploadResponse
)
from services.conversation import conversation_manager
from services.llm import llm_service
from services.file_processor import file_processor

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """Get list of available LLM models"""
    try:
        models = llm_service.get_available_models()
        logger.info(f"Returned {len(models)} available models")
        return models
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available models")

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations():
    """Get all conversations"""
    try:
        conversations = conversation_manager.get_all_conversations()
        logger.info(f"Returned {len(conversations)} conversations")
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    model_provider: ModelProvider,
    model_name: str,
    title: str = "New Chat"
):
    """Create a new conversation"""
    try:
        conversation = conversation_manager.create_conversation(
            model_provider=model_provider,
            model_name=model_name,
            title=title
        )
        logger.info(f"Created conversation {conversation.id}")
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    try:
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        logger.info(f"Retrieved conversation {conversation_id}")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        success = conversation_manager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        logger.info(f"Deleted conversation {conversation_id}")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")

@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(conversation_id: str, request: ChatRequest):
    """Send a message in a conversation"""
    try:
        # Get or create conversation
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            conversation = conversation_manager.create_conversation(
                model_provider=request.model_provider,
                model_name=request.model_name
            )
            conversation_id = conversation.id
        
        # Add file to conversation's user_uploaded_files list if provided
        if request.file_content:
            conversation_manager.add_file_to_conversation(conversation_id, request.file_content)
        
        # Add user message
        user_message = conversation_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=request.message,
            file_attachment=request.file_content
        )
        
        if not user_message:
            raise HTTPException(status_code=500, detail="Failed to add user message")
        
        # Prepare messages for LLM
        messages = []
        for msg in conversation.messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Generate AI response
        logger.info(f"Generating response for conversation {conversation_id} with {request.model_provider}/{request.model_name}")
        ai_response = await llm_service.generate_response(
            messages=messages,
            provider=request.model_provider,
            model_name=request.model_name,
            uploaded_files=conversation.user_uploaded_files
        )
        
        # Add AI response to conversation
        assistant_message = conversation_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            model_used=f"{request.model_provider.value}/{request.model_name}"
        )
        
        if not assistant_message:
            raise HTTPException(status_code=500, detail="Failed to add assistant message")
        
        logger.info(f"Successfully generated response for conversation {conversation_id}")
        return ChatResponse(message=assistant_message, conversation_id=conversation_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Process the file
        content = await file_processor.process_file(file)
        file_info = file_processor.get_file_info(file)
        
        response = FileUploadResponse(
            filename=file_info["filename"],
            content=content,
            size=file_info["size"] or 0,
            type=file_info["extension"] or ""
        )
        
        logger.info(f"Successfully processed uploaded file: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/message", response_model=ChatResponse)
async def send_standalone_message(request: ChatRequest):
    """Send a standalone message (creates new conversation if needed)"""
    try:
        # Use existing conversation or create new one
        if request.conversation_id:
            conversation_id = request.conversation_id
        else:
            conversation = conversation_manager.create_conversation(
                model_provider=request.model_provider,
                model_name=request.model_name
            )
            conversation_id = conversation.id
        
        # Forward to the existing endpoint
        return await send_message(conversation_id, request)
        
    except Exception as e:
        logger.error(f"Error sending standalone message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")