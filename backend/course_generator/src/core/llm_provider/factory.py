import os
from typing import Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from .interfaces import ProviderType, ModelCapability

class LLMFactory:
    """
    Centralized factory for creating provider-agnostic LangChain ChatModels.
    Implements a Singleton pattern to avoid repeated initialization.
    """
    
    _instances: Dict[str, BaseChatModel] = {}
    
    # Internal mapping of capabilities to specific models per provider
    _MODEL_MAP = {
        ProviderType.GROQ: {
            ModelCapability.FAST_JSON: "llama-3.1-8b-instant",
            ModelCapability.COMPLEX_REASONING: "llama-3.3-70b-versatile",
        },
        ProviderType.GEMINI: {
            ModelCapability.FAST_JSON: "gemini-2.0-flash",
            ModelCapability.COMPLEX_REASONING: "gemini-2.5-pro",
        },
        ProviderType.OPENAI: {
            ModelCapability.FAST_JSON: "gpt-4o-mini",
            ModelCapability.COMPLEX_REASONING: "gpt-4o",
        }
    }

    @classmethod
    def get_provider(cls) -> ProviderType:
        """Get the configured default provider from environment, fallback to Groq."""
        provider_str = os.getenv("DEFAULT_LLM_PROVIDER", "groq").lower()
        try:
            return ProviderType(provider_str)
        except ValueError:
            print(f"[LLMFactory] Warning: Unknown provider '{provider_str}', falling back to Groq.")
            return ProviderType.GROQ

    @classmethod
    def get_llm(
        cls, 
        capability: ModelCapability = ModelCapability.FAST_JSON,
        temperature: float = 0.2,
        provider_override: Optional[ProviderType] = None
    ) -> BaseChatModel:
        """
        Instantiates and returns a configured LangChain BaseChatModel.
        Uses a Singleton cache to prevent repeated initializations.
        """
        provider = provider_override or cls.get_provider()
        
        # Resolve the actual model name based on provider and capability
        model_name = cls._MODEL_MAP[provider].get(capability)
        if not model_name:
            raise ValueError(f"Provider {provider} does not support capability {capability}")
            
        cache_key = f"{provider.value}_{model_name}_{temperature}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
            
        print(f"[LLMFactory] Initializing LLM | Provider: {provider.value.upper()} | Model: {model_name}")

        llm: BaseChatModel
        if provider == ProviderType.GROQ:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                max_retries=3,
            )
            
        elif provider == ProviderType.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY is not set in the environment.")
                
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_retries=3,
            )
            
        elif provider == ProviderType.OPENAI:
            from langchain_openai import ChatOpenAI
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY is not set in the environment.")
                
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_retries=3,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
        cls._instances[cache_key] = llm
        return llm

    @classmethod
    def get_fallback_llm(
        cls, 
        capability: ModelCapability = ModelCapability.FAST_JSON,
        temperature: float = 0.2
    ) -> BaseChatModel:
        """
        Returns a stable fallback provider (e.g. Gemini) if the primary provider fails.
        """
        # We default to Gemini as a highly reliable, high-rate-limit fallback
        return cls.get_llm(
            capability=capability, 
            temperature=temperature, 
            provider_override=ProviderType.GEMINI
        )
