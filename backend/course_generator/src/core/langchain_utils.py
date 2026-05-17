import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_base_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.2, max_tokens: int = 500) -> ChatGroq:
    """
    Returns a configured ChatGroq instance.
    Uses the GROQ_API_KEY from the environment automatically.
    """
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=3,  # LangChain natively handles retries on Rate Limits and transient errors
    )

def get_json_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.2) -> ChatGroq:
    """
    Returns a ChatGroq instance configured specifically for JSON/structured outputs.
    Note: When using `.with_structured_output()`, LangChain often forces JSON mode anyway.
    """
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_retries=3,
    )

def build_transcript_retriever(transcript_text: str):
    """
    Splits the transcript and builds an in-memory FAISS VectorStore.
    Returns a retriever that can be used to fetch relevant chunks for a given query (e.g. lesson title).
    """
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from course_generator.src.pipeline.chunking_service import chunking_service
    
    # 1. Chunk the transcript into smaller pieces
    print("[RAG] Splitting transcript into chunks...")
    chunks = chunking_service.chunk_transcript(transcript_text)
    
    # 2. Initialize HuggingFace Embeddings (runs locally, no API key needed)
    print("[RAG] Initializing Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 3. Build FAISS index
    print(f"[RAG] Building FAISS VectorStore with {len(chunks)} chunks...")
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    
    # 4. Return as retriever (fetch top 3 chunks)
    return vectorstore.as_retriever(search_kwargs={"k": 3})
