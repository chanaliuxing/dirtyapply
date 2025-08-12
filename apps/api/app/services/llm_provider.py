"""
LLM Provider Service
Implements multiple AI providers including DeepSeek via NVIDIA
Follows Golden Rules - no hard-coded secrets, safe logging
"""

from typing import Optional, Dict, Any, List, AsyncIterator
from abc import ABC, abstractmethod
from openai import OpenAI, AsyncOpenAI
import anthropic
import structlog
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Generate a single response"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("OpenAI provider initialized")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Generate response using OpenAI API"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise

class DeepSeekNvidiaProvider(LLMProvider):
    """DeepSeek via NVIDIA API provider"""
    
    def __init__(self, api_key: str):
        # Use OpenAI client with NVIDIA base URL
        self.client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        logger.info("DeepSeek NVIDIA provider initialized")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "deepseek-ai/deepseek-r1",
        temperature: float = 0.6,
        top_p: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Generate response using DeepSeek via NVIDIA API"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek NVIDIA API error: {e}")
            raise
    
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "deepseek-ai/deepseek-r1",
        temperature: float = 0.6,
        top_p: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response using DeepSeek via NVIDIA"""
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"DeepSeek NVIDIA streaming error: {e}")
            raise

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        logger.info("Anthropic provider initialized")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Generate response using Anthropic API"""
        
        try:
            # Convert OpenAI-style messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                system=system_message if system_message else "You are a helpful assistant.",
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        
        try:
            # Convert messages format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            async with self.client.messages.stream(
                model=model,
                system=system_message if system_message else "You are a helpful assistant.",
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise

class RuleBasedProvider(LLMProvider):
    """Rule-based provider for offline operation"""
    
    def __init__(self):
        logger.info("Rule-based provider initialized (offline mode)")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Generate rule-based response"""
        
        # Simple rule-based logic for demo
        user_message = messages[-1]["content"].lower()
        
        if "resume" in user_message or "jtr" in user_message:
            return "Rule-based JTR analysis: This appears to be a resume tailoring request. In a full implementation, this would analyze job requirements and generate tailored resume content."
        
        elif "action plan" in user_message or "form" in user_message:
            return "Rule-based action plan: This appears to be a form-filling request. In a full implementation, this would generate specific selectors and automation steps."
        
        else:
            return "Rule-based response: I can help with resume tailoring (JTR) and action plan generation using pre-programmed rules."
    
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming rule-based response"""
        
        response = await self.generate_response(messages, **kwargs)
        
        # Simulate streaming by yielding chunks
        words = response.split()
        for word in words:
            yield word + " "

class LLMService:
    """LLM service factory and manager"""
    
    def __init__(self):
        self.settings = get_settings()
        self._provider: Optional[LLMProvider] = None
    
    def get_provider(self) -> LLMProvider:
        """Get the configured LLM provider"""
        
        if self._provider is None:
            self._provider = self._create_provider()
        
        return self._provider
    
    def _create_provider(self) -> LLMProvider:
        """Create provider based on configuration"""
        
        provider_type = self.settings.llm_provider
        
        try:
            if provider_type == "openai":
                if not self.settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                return OpenAIProvider(self.settings.openai_api_key)
            
            elif provider_type == "deepseek-nvidia":
                if not self.settings.deepseek_nvidia_api_key:
                    raise ValueError("DeepSeek NVIDIA API key not configured")
                return DeepSeekNvidiaProvider(self.settings.deepseek_nvidia_api_key)
            
            elif provider_type == "anthropic":
                if not self.settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                return AnthropicProvider(self.settings.anthropic_api_key)
            
            elif provider_type == "none":
                return RuleBasedProvider()
            
            else:
                logger.warning(f"Unknown LLM provider: {provider_type}, falling back to rule-based")
                return RuleBasedProvider()
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider {provider_type}: {e}")
            logger.info("Falling back to rule-based provider")
            return RuleBasedProvider()

# Global service instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

# Convenience functions
async def generate_llm_response(
    messages: List[Dict[str, str]], 
    **kwargs
) -> str:
    """Generate LLM response using configured provider"""
    service = get_llm_service()
    provider = service.get_provider()
    return await provider.generate_response(messages, **kwargs)

async def generate_llm_stream(
    messages: List[Dict[str, str]], 
    **kwargs
) -> AsyncIterator[str]:
    """Generate streaming LLM response"""
    service = get_llm_service()
    provider = service.get_provider()
    async for chunk in provider.generate_stream(messages, **kwargs):
        yield chunk