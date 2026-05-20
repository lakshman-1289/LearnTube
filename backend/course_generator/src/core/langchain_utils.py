import os
from langchain_core.language_models.chat_models import BaseChatModel
from course_generator.src.core.llm_provider.factory import LLMFactory
from course_generator.src.core.llm_provider.interfaces import ModelCapability
from dotenv import load_dotenv

load_dotenv()

import re
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser

class JSONCleanupParser(BaseOutputParser):
    """Strips markdown and attempts to fix basic JSON issues before passing to Pydantic."""
    pydantic_parser: PydanticOutputParser

    def parse(self, text: str):
        # 1. Strip markdown ```json ... ``` blocks
        text = text.strip()
        if text.startswith("```"):
            match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        
        # 2. Strip hallucinated <function> tags often produced by small Groq models
        if "<function=" in text:
            match = re.search(r"<function=[^>]+>(.*?)</function>", text, re.DOTALL)
            if not match:
                match = re.search(r"<function=[^>]+>(.*)", text, re.DOTALL)
            if match:
                text = match.group(1).strip()

        # Pass the cleaned text to the actual Pydantic parser
        return self.pydantic_parser.parse(text)

def build_robust_structured_chain(prompt, pydantic_schema, primary_llm=None):
    """
    Builds a highly robust multi-stage structured output chain.
    Stage 1: JSON Mode + Custom Regex Cleanup (bypasses brittle API tool calling).
    Stage 2: Parachute to Gemini Reasoning Model using native tool calling if Stage 1 completely fails.
    """
    if not primary_llm:
        primary_llm = LLMFactory.get_llm(ModelCapability.FAST_JSON)
        
    pydantic_parser = PydanticOutputParser(pydantic_object=pydantic_schema)
    cleanup_parser = JSONCleanupParser(pydantic_parser=pydantic_parser)
    
    # 1. Primary Strategy: JSON Mode (forces C-engine to output raw JSON tokens)
    json_llm = primary_llm
    if hasattr(primary_llm, "bind"):
        try:
            json_llm = primary_llm.bind(response_format={"type": "json_object"})
        except Exception:
            pass
            
    primary_chain = prompt | json_llm | cleanup_parser
    
    # 2. Fallback Strategy: Gemini Reasoning Model
    reasoning_llm = LLMFactory.get_fallback_llm(ModelCapability.COMPLEX_REASONING)
    fallback_chain = prompt | reasoning_llm.with_structured_output(pydantic_schema)
    
    # Retry the fast JSON model twice, if it keeps returning broken schemas, parachute to Gemini
    return primary_chain.with_retry(stop_after_attempt=2).with_fallbacks([fallback_chain])

def get_base_llm(temperature: float = 0.2) -> BaseChatModel:
    """
    Returns a configured BaseChatModel instance using the central LLMFactory.
    """
    return LLMFactory.get_llm(
        capability=ModelCapability.COMPLEX_REASONING,
        temperature=temperature
    )

def get_json_llm(temperature: float = 0.2) -> BaseChatModel:
    """
    Returns a BaseChatModel instance configured specifically for JSON/structured outputs.
    """
    return LLMFactory.get_llm(
        capability=ModelCapability.FAST_JSON,
        temperature=temperature
    )

def chunk_transcript_for_rag(transcript_text: str) -> list[str]:
    """
    Chunks a transcript using RecursiveCharacterTextSplitter.
    Ideal chunk size 2000, overlap 200 for RAG context windows.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_text(transcript_text)


def build_transcript_retriever(chunks: list[str]):
    """
    Builds an in-memory FAISS VectorStore from pre-computed chunks.
    Configures MMR (Maximal Marginal Relevance) for context diversity.
    """
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    
    print("[RAG] Initializing Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print(f"[RAG] Building FAISS VectorStore with {len(chunks)} chunks...")
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    
    # Use MMR (Maximal Marginal Relevance) to avoid duplicate context retrieval
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 8}
    )
