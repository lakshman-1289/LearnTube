import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService:
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # We use tiktoken natively inside LangChain's text splitter
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )

    def clean_transcript(self, transcript: str) -> str:
        content = re.sub(r'\b(um|uh|ah|like|you know)\b', '', transcript, flags=re.IGNORECASE)
        content = re.sub(r'\b(gonna)\b', 'going to', content, flags=re.IGNORECASE)
        content = re.sub(r'\b(wanna)\b', 'want to', content, flags=re.IGNORECASE)
        content = re.sub(r'\s+', ' ', content)
        return content.strip()

    def chunk_transcript(self, transcript_text: str) -> List[str]:
        """
        Takes raw transcript and outputs a list of semantically meaningful chunks (approx bounded by token limits)
        Uses LangChain RecursiveCharacterTextSplitter natively.
        """
        cleaned_text = self.clean_transcript(transcript_text)
        return self.splitter.split_text(cleaned_text)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using the tiktoken encoding tied to the splitter."""
        # RecursiveCharacterTextSplitter exposes a _length_function when from_tiktoken_encoder is used
        try:
            return self.splitter._length_function(text)
        except:
            return len(text) // 4

    def smart_chunk_transcript(
        self,
        transcript_text: str,
        prompt_template: str,
        max_output_tokens: int = 2000,
        token_limit: int = 8000,
        buffer_tokens: int = 50,
        min_chunk_tokens: int = 200
    ) -> List[str]:
        """
        Create sentence-aware chunks that ensure (prompt + chunk + max_output_tokens) <= token_limit.
        Uses LangChain RecursiveCharacterTextSplitter dynamically.
        """
        cleaned_text = self.clean_transcript(transcript_text)
        
        # Estimate prompt overhead
        prompt_overhead = prompt_template.replace('{transcript}', '')
        overhead_tokens = self.estimate_tokens(prompt_overhead)
        
        max_allowed_for_chunk = max(100, token_limit - overhead_tokens - max_output_tokens - buffer_tokens)
        
        # Create a dynamic splitter specifically for this token limit
        dynamic_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=max_allowed_for_chunk,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )
        
        return dynamic_splitter.split_text(cleaned_text)

chunking_service = ChunkingService()

