from enum import Enum

class ProviderType(str, Enum):
    """Supported LLM Providers"""
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"

class ModelCapability(str, Enum):
    """
    Capabilities used to route to specific models.
    Instead of asking for 'llama-3.1', business logic asks for a capability.
    """
    FAST_JSON = "fast_json"          # High speed, strict JSON adherence
    COMPLEX_REASONING = "complex"    # Heavy reasoning, slower, higher context
    EMBEDDINGS = "embeddings"        # Vector embeddings
