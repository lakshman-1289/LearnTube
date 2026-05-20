import os
from aiolimiter import AsyncLimiter
from course_generator.src.core.llm_provider.factory import LLMFactory
from course_generator.src.core.llm_provider.interfaces import ProviderType

class RateLimiter:
    """
    Provides dynamic rate limiting based on the currently active LLM provider.
    Groq free/production tiers often restrict to 6000 TPM or 30 RPM.
    """
    _limiter = None
    
    @classmethod
    def get_limiter(cls) -> AsyncLimiter:
        if cls._limiter is None:
            provider = LLMFactory.get_provider()
            if provider == ProviderType.GROQ:
                # Groq limit: 30 requests per 60 seconds
                cls._limiter = AsyncLimiter(30, 60)
            else:
                # Gemini/OpenAI: 150 requests per 60 seconds
                cls._limiter = AsyncLimiter(150, 60)
        return cls._limiter
        
    @classmethod
    def get_semaphore_limit(cls) -> int:
        """Returns the optimal concurrency limit."""
        provider = LLMFactory.get_provider()
        return 2 if provider == ProviderType.GROQ else 5
