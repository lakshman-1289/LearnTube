from typing import Dict, List
from models.pipeline_schemas import TopicList
from course_generator.src.core.langchain_utils import get_json_llm
from course_generator.src.pipeline.prompts import Prompts
import asyncio

class TopicExtractor:
    def __init__(self, llm=None):
        # Use provided LLM or get the default JSON-configured ChatGroq
        self.llm = llm or get_json_llm()
        
        # Create the LCEL chain: Prompt | LLM(with structured output)
        self.chain = (Prompts.TOPIC_EXTRACTION | self.llm.with_structured_output(TopicList, method="json_mode")).with_retry(stop_after_attempt=3)

    async def extract_topics(self, transcript_text: str) -> TopicList:
        """
        Extracts topics from the given plain transcript text in chunks to avoid rate limits.
        Uses LangChain LCEL for prompt formatting and structured output parsing.
        """
        from course_generator.src.pipeline.chunking_service import chunking_service
        import os

        # Determine safe token limit per request (default to 1500 to heavily reduce TPM load)
        safe_limit = int(os.getenv("GROQ_SAFE_TOKEN_LIMIT", "1500"))
        max_output_tokens = 500

        # We will keep the custom chunking for now until Phase 2 (TextSplitters)
        # We pass a simple string template since smart_chunk_transcript expects a format string.
        # Once Phase 2 is done, this will just use RecursiveCharacterTextSplitter.
        dummy_prompt = "Topics:\n{transcript}"
        chunks = chunking_service.smart_chunk_transcript(
            transcript_text=transcript_text,
            prompt_template=dummy_prompt,
            max_output_tokens=max_output_tokens,
            token_limit=safe_limit,
            buffer_tokens=50
        )
        all_topics = []
        
        for i, chunk in enumerate(chunks):
            print(f"[PIPELINE] 🧩 Extracting topics from chunk {i+1}/{len(chunks)}...")
            
            # LCEL execution
            result: TopicList = await self.chain.ainvoke({"transcript": chunk})
            
            all_topics.extend(result.topics)
            
            # Stay under 12k TPM rate limits roughly
            if i < len(chunks) - 1:
                print("[PIPELINE] ⏱️ Sleeping 12s to respect API rate limits...")
                await asyncio.sleep(12)
                
        return TopicList(topics=all_topics)

