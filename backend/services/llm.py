import logging
from typing import List, Dict
from models.agent import AgentRunResultContext
from services.agent import ROUTER_AGENT
import openai
import anthropic
from config.settings import get_settings
from models.chat import ModelProvider, ModelInfo
from agents import Runner


logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with different LLM providers"""
    
    def __init__(self):
        self.settings = get_settings()
        self._init_clients()
        self._init_models()
        self.agent = ROUTER_AGENT
        self.agent_context = AgentRunResultContext()
    
    def _init_clients(self):
        """Initialize API clients"""
        self.openai_client = None
        self.anthropic_client = None
        
        logger.info(f"OpenAI API key starts with: {self.settings.openai_api_key[:10]}...")
        logger.info(f"Anthropic API key starts with: {self.settings.anthropic_api_key[:10]}...")
        
        # Check if OpenAI API key is valid (not placeholder)
        if self.settings.openai_api_key and not self.settings.openai_api_key.startswith("your_"):
            try:
                # Use the modern OpenAI API (v1.0+) with explicit http_client to avoid proxy issues
                import httpx
                http_client = httpx.Client()
                self.openai_client = openai.OpenAI(
                    api_key=self.settings.openai_api_key,
                    http_client=http_client
                )
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        else:
            logger.info("⚠️ No valid OpenAI API key configured")
        
        # Check if Anthropic API key is valid (not placeholder)
        if self.settings.anthropic_api_key and not self.settings.anthropic_api_key.startswith("your_"):
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
                logger.info("✅ Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Anthropic client: {e}")
        else:
            logger.info("⚠️ No valid Anthropic API key configured")
    
    def _init_models(self):
        """Initialize available models"""
        self.static_anthropic_models = [
            # Anthropic models (static for now)
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
        # OpenAI models will be fetched dynamically
        self.openai_models_cache = []
        self.openai_models_last_fetched = None
        logger.info("Model system initialized - OpenAI models will be fetched dynamically")
    
    def _fetch_openai_models(self) -> List[ModelInfo]:
        """Fetch available OpenAI models from API"""
        if not self.openai_client:
            return []
        
        try:
            # Check cache validity (cache for 1 hour)
            from datetime import datetime, timedelta
            now = datetime.now()
            if (self.openai_models_last_fetched and 
                now - self.openai_models_last_fetched < timedelta(hours=1)):
                return self.openai_models_cache
            
            logger.info("Fetching OpenAI models from API...")
            models_response = self.openai_client.models.list()
            
            # Add ALL models from OpenAI API without filtering
            all_models = []
            for model in models_response.data:
                model_id = model.id
                
                # Create intelligent display name and description
                display_name = model_id
                description = "OpenAI Model"
                
                if 'gpt-5' in model_id.lower():
                    display_name = f"GPT-5 ({model_id})"
                    description = "Latest GPT-5 model - next generation AI"
                elif 'gpt-4o' in model_id.lower():
                    display_name = f"GPT-4o ({model_id})"
                    description = "Latest GPT-4o model - multimodal capabilities"
                elif 'gpt-4' in model_id.lower():
                    if 'turbo' in model_id.lower():
                        display_name = f"GPT-4 Turbo ({model_id})"
                        description = "GPT-4 Turbo - fast and capable"
                    else:
                        display_name = f"GPT-4 ({model_id})"
                        description = "GPT-4 - highly capable model"
                elif 'gpt-3.5' in model_id.lower():
                    display_name = f"GPT-3.5 ({model_id})"
                    description = "GPT-3.5 - fast and efficient"
                elif 'dall-e' in model_id.lower():
                    display_name = f"DALL-E ({model_id})"
                    description = "Image generation model"
                elif 'whisper' in model_id.lower():
                    display_name = f"Whisper ({model_id})"
                    description = "Speech to text model"
                elif 'tts' in model_id.lower():
                    display_name = f"TTS ({model_id})"
                    description = "Text to speech model"
                elif 'embedding' in model_id.lower():
                    display_name = f"Embedding ({model_id})"
                    description = "Text embedding model"
                else:
                    display_name = model_id
                    description = f"OpenAI {model_id} model"
                
                all_models.append(ModelInfo(
                    provider=ModelProvider.OPENAI,
                    name=model_id,
                    display_name=display_name,
                    description=description
                ))
            
            # Sort models by preference (GPT-5 first, then GPT-4o, GPT-4, etc.)
            def model_priority(model):
                name = model.name.lower()
                if 'gpt-5' in name:
                    return 0
                elif 'gpt-4o' in name:
                    return 1
                elif 'gpt-4' in name and 'turbo' in name:
                    return 2
                elif 'gpt-4' in name:
                    return 3
                elif 'gpt-3.5' in name:
                    return 4
                elif 'chat' in name or 'gpt' in name:
                    return 5
                else:
                    return 6
            
            all_models.sort(key=model_priority)
            
            logger.info(f"Total models fetched: {len(all_models)}")
            if any('gpt-5' in model.name.lower() for model in all_models):
                gpt5_count = len([m for m in all_models if 'gpt-5' in m.name.lower()])
                logger.info(f"GPT-5 models included: {gpt5_count}")
            
            # Update cache
            self.openai_models_cache = all_models
            self.openai_models_last_fetched = now
            
            logger.info(f"Successfully fetched {len(all_models)} OpenAI models")
            return all_models
            
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI models: {e}")
            # Return cached models if available, otherwise return empty list
            return self.openai_models_cache if self.openai_models_cache else []
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models based on configured API keys"""
        available = []
        
        # Add OpenAI models if client is available
        if self.openai_client:
            openai_models = self._fetch_openai_models()
            available.extend(openai_models)
        
        # Add Anthropic models if client is available
        if self.anthropic_client:
            available.extend(self.static_anthropic_models)
        
        logger.debug(f"Returning {len(available)} available models")
        return available
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              provider: ModelProvider, model_name: str) -> str:
        """Generate response from LLM"""
        try:
            if provider == ModelProvider.OPENAI:
                # return await self._generate_openai_response(messages, model_name)
                return await self._generate_openai_agent_response(messages, model_name)
            elif provider == ModelProvider.ANTHROPIC:
                return await self._generate_anthropic_response(messages, model_name)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Error generating response with {provider}/{model_name}: {e}")
            raise

    async def _generate_openai_agent_response(self, messages: List[Dict[str, str]], model_name: str) -> str:
            logger.debug(f"Agent Input: {messages}")
            result = await Runner.run(starting_agent=self.agent,
                                      input=messages,
                                      context=self.agent_context)
            return result.final_output
    
    async def _generate_openai_response(self, messages: List[Dict[str, str]], model_name: str) -> str:
        """Generate response using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        logger.info(f"Generating OpenAI response with model {model_name}")
        logger.debug(f"Input messages: {messages}")
        
        try:
            # Use the modern OpenAI API
            # GPT-5 models have different parameter requirements
            if 'gpt-5' in model_name.lower():
                # GPT-5 models: use max_completion_tokens and don't support custom temperature
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_completion_tokens=self.settings.max_output_tokens
                )
            else:
                # Other models: use standard parameters
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=self.settings.max_output_tokens
                )
            
            # Modern OpenAI response format
            logger.debug(f"OpenAI response object: {response}")
            
            if not response.choices:
                logger.error("No choices in OpenAI response")
                return "I apologize, but I couldn't generate a response. Please try again."
            
            choice = response.choices[0]
            logger.debug(f"First choice: {choice}")
            logger.info(f"OpenAI finish_reason: {choice.finish_reason}")
            
            if choice.finish_reason == "content_filter":
                logger.warning("OpenAI response was filtered by content policy")
                return "I apologize, but my response was filtered by content policy. Please try rephrasing your question."
            
            if choice.finish_reason in ["length", "max_tokens"]:
                logger.warning(f"OpenAI response was cut off due to {choice.finish_reason}")
                # Still return the partial content if available
            
            content = choice.message.content
            logger.info(f"OpenAI raw content: {repr(content)}")
            
            if content is None:
                logger.error(f"OpenAI returned None content. Choice: {choice}")
                return "I apologize, but I received an empty response. Please try again."
            
            if not content.strip():
                logger.warning("OpenAI returned empty content")
                return "I apologize, but I received an empty response. Please try again."
            
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
                max_tokens=self.settings.max_output_tokens
            )
            
            content = response.content[0].text
            logger.info(f"Generated Anthropic response: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

# Global LLM service instance
llm_service = LLMService()