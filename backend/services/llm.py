import logging
from typing import List, Dict, Any, Optional
import openai
import anthropic
from config.settings import get_settings
from models.chat import ModelProvider, ModelInfo

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with different LLM providers"""
    
    def __init__(self):
        self.settings = get_settings()
        self._init_clients()
        self._init_models()
    
    def _init_clients(self):
        """Initialize API clients"""
        self.openai_client = None
        self.anthropic_client = None
        
        if self.settings.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        if self.settings.anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def _init_models(self):
        """Initialize available models"""
        self.available_models = [
            # OpenAI models
            ModelInfo(
                provider=ModelProvider.OPENAI,
                name="gpt-4-turbo-preview",
                display_name="GPT-4 Turbo",
                description="Most capable GPT-4 model"
            ),
            ModelInfo(
                provider=ModelProvider.OPENAI,
                name="gpt-4",
                display_name="GPT-4",
                description="Standard GPT-4 model"
            ),
            ModelInfo(
                provider=ModelProvider.OPENAI,
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                description="Fast and efficient model"
            ),
            # Anthropic models
            ModelInfo(
                provider=ModelProvider.ANTHROPIC,
                name="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                description="Most capable Claude model"
            ),
            ModelInfo(
                provider=ModelProvider.ANTHROPIC,
                name="claude-3-sonnet-20240229",
                display_name="Claude 3 Sonnet",
                description="Balanced Claude model"
            ),
            ModelInfo(
                provider=ModelProvider.ANTHROPIC,
                name="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                description="Fast Claude model"
            ),
        ]
        logger.info(f"Initialized {len(self.available_models)} available models")
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models based on configured API keys"""
        available = []
        
        for model in self.available_models:
            if model.provider == ModelProvider.OPENAI and self.openai_client:
                available.append(model)
            elif model.provider == ModelProvider.ANTHROPIC and self.anthropic_client:
                available.append(model)
        
        logger.debug(f"Returning {len(available)} available models")
        return available
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              provider: ModelProvider, model_name: str) -> str:
        """Generate response from LLM"""
        try:
            if provider == ModelProvider.OPENAI:
                return await self._generate_openai_response(messages, model_name)
            elif provider == ModelProvider.ANTHROPIC:
                return await self._generate_anthropic_response(messages, model_name)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Error generating response with {provider}/{model_name}: {e}")
            raise
    
    async def _generate_openai_response(self, messages: List[Dict[str, str]], model_name: str) -> str:
        """Generate response using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        logger.info(f"Generating OpenAI response with model {model_name}")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            logger.info(f"Generated OpenAI response: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic_response(self, messages: List[Dict[str, str]], model_name: str) -> str:
        """Generate response using Anthropic API"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        logger.info(f"Generating Anthropic response with model {model_name}")
        
        try:
            # Convert messages to Anthropic format
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.anthropic_client.messages.create(
                model=model_name,
                system=system_message if system_message else "You are a helpful assistant.",
                messages=anthropic_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.content[0].text
            logger.info(f"Generated Anthropic response: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

# Global LLM service instance
llm_service = LLMService()