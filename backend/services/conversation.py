import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from models.chat import Conversation, Message, MessageRole, ModelProvider

logger = logging.getLogger(__name__)

class ConversationManager:
    """In-memory conversation management"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        logger.info("ConversationManager initialized")
    
    def create_conversation(self, model_provider: ModelProvider, model_name: str, title: str = "New Chat") -> Conversation:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            messages=[],
            created_at=now,
            updated_at=now,
            model_provider=model_provider,
            model_name=model_name,
            user_uploaded_files=[]
        )
        
        self.conversations[conversation_id] = conversation
        logger.info(f"Created conversation {conversation_id} with {model_provider}/{model_name}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        conversation = self.conversations.get(conversation_id)
        if conversation:
            logger.debug(f"Retrieved conversation {conversation_id}")
        else:
            logger.warning(f"Conversation {conversation_id} not found")
        return conversation
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations sorted by updated_at descending"""
        conversations = sorted(
            self.conversations.values(),
            key=lambda c: c.updated_at,
            reverse=True
        )
        logger.debug(f"Retrieved {len(conversations)} conversations")
        return conversations
    
    def add_message(self, conversation_id: str, role: MessageRole, content: str, 
                   model_used: Optional[str] = None, file_attachment: Optional[str] = None) -> Optional[Message]:
        """Add a message to a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Cannot add message to non-existent conversation {conversation_id}")
            return None
        
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            role=role,
            content=content,
            timestamp=datetime.now(),
            model_used=model_used,
            file_attachment=file_attachment
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        
        # Update conversation title based on first user message
        if len(conversation.messages) == 1 and role == MessageRole.USER:
            conversation.title = content[:50] + "..." if len(content) > 50 else content
        
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message
    
    def add_file_to_conversation(self, conversation_id: str, file_content: str) -> bool:
        """Add file content to conversation's user_uploaded_files list"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Cannot add file to non-existent conversation {conversation_id}")
            return False
        
        conversation.user_uploaded_files.append(file_content)
        conversation.updated_at = datetime.now()
        
        logger.info(f"Added file to conversation {conversation_id}, total files: {len(conversation.user_uploaded_files)}")
        return True
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        logger.warning(f"Attempted to delete non-existent conversation {conversation_id}")
        return False
    
    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """Get message history for a conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            logger.debug(f"Retrieved {len(conversation.messages)} messages for conversation {conversation_id}")
            return conversation.messages
        return []

# Global conversation manager instance
conversation_manager = ConversationManager()