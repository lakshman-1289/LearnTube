from typing import Dict, List
from models.pipeline_schemas import TopicList
from course_generator.src.core.langchain_utils import get_json_llm, get_base_llm, chunk_transcript_for_rag, build_robust_structured_chain
from course_generator.src.core.rate_limiter import RateLimiter
from course_generator.src.pipeline.prompts import Prompts
import asyncio

class TopicExtractor:
    def __init__(self, llm=None):
        # Use provided LLM or get the default JSON-configured ChatModel (Groq)
        self.llm = llm or get_json_llm()
        
        # Map Chain: Extract micro-topics from individual chunks
        self.map_chain = build_robust_structured_chain(Prompts.MAP_TOPIC_EXTRACTION, TopicList, self.llm)
        
        # Reduce Chain: Consolidate micro-topics into a unified curriculum
        # Kept on Groq to preserve free Gemini API quotas
        self.reduce_chain = build_robust_structured_chain(Prompts.TOPIC_EXTRACTION, TopicList, self.llm)

    def _get_representative_chunks(self, chunks: List[str], max_clusters: int = 15) -> List[str]:
        """
        Uses Semantic Compression (KMeans clustering on embeddings) to find representative chunks.
        This drastically reduces Map-phase LLM calls while preserving curriculum structure.
        """
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.metrics import pairwise_distances_argmin_min
        from langchain_huggingface import HuggingFaceEmbeddings

        if len(chunks) <= max_clusters:
            return chunks
            
        print(f"[PIPELINE] 🧠 Semantically compressing {len(chunks)} chunks...")
        
        # 1. Embed all chunks using a fast local model
        embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        embeddings = embeddings_model.embed_documents(chunks)
        X = np.array(embeddings)
        
        # 2. Cluster the embeddings
        num_clusters = min(max_clusters, len(chunks))
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        kmeans.fit(X)
        
        # 3. Find the closest chunk to each cluster centroid
        closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, X)
        
        # Extract the representative chunks and sort them chronologically
        representative_indices = sorted(closest.tolist())
        representative_chunks = [chunks[i] for i in representative_indices]
        
        print(f"[PIPELINE] ✨ Semantic compression complete. Reduced to {len(representative_chunks)} representative chunks.")
        return representative_chunks

    async def extract_topics(self, transcript_text: str) -> TopicList:
        """
        Extracts topics using a scalable Map-Reduce pattern.
        """
        # 1. Chunk transcript safely using RAG text splitters
        all_chunks = chunk_transcript_for_rag(transcript_text)
        print(f"[PIPELINE] 🗺️ Generated {len(all_chunks)} total chunks.")

        # 2. Semantic Compression: Find representative chunks to avoid Map-phase bloat
        representative_chunks = self._get_representative_chunks(all_chunks, max_clusters=15)
        print(f"[PIPELINE] 🗺️ Mapping over {len(representative_chunks)} representative chunks concurrently...")

        # 3. Map Phase: Extract micro-topics concurrently with rate limiting
        sem = asyncio.Semaphore(RateLimiter.get_semaphore_limit())
        limiter = RateLimiter.get_limiter()

        async def map_chunk(chunk: str):
            async with sem:
                async with limiter:
                    try:
                        result: TopicList = await self.map_chain.ainvoke({"transcript": chunk})
                        # Strictly bound the topics size to protect the reduce phase context window
                        return result.topics[:3] if result and result.topics else []
                    except Exception as e:
                        print(f"[PIPELINE] ⚠️ Map chunk failed: {e}")
                        # Graceful degradation: skip the bad chunk rather than crashing the pipeline
                        return []

        # 4. Process Map tasks in strict batches to prevent TPM rate limit explosions
        all_micro_topics = []
        batch_size = 5  # Safe batch size to prevent hitting 6000 TPM Groq limit
        
        for i in range(0, len(representative_chunks), batch_size):
            batch = representative_chunks[i : i + batch_size]
            print(f"[PIPELINE] ⏳ Processing chunk batch {i+1} to {min(i+len(batch), len(representative_chunks))} of {len(representative_chunks)}...")
            
            batch_results = await asyncio.gather(*(map_chunk(c) for c in batch))
            
            # Flatten the list of lists for this batch
            for sublist in batch_results:
                if sublist:
                    all_micro_topics.extend(sublist)
                    
            # Explicit TPM Cooldown if there are more chunks
            if i + batch_size < len(representative_chunks):
                print("[PIPELINE] ⏱️ TPM Cooldown: Sleeping 12 seconds before next chunk batch...")
                await asyncio.sleep(12)
        
        print(f"[PIPELINE] 🔄 Reduced {len(all_micro_topics)} micro-topics. Consolidating...")
        
        # Fallback if no topics found
        if not all_micro_topics:
            raise ValueError("Map phase failed to extract any micro-topics.")

        # 4. Hierarchical Reduce Phase (to respect Groq 6000 TPM limits)
        MAX_TOPICS_PER_REDUCE = 60  # Approximately 1800 tokens, perfectly safe for Groq
        if len(all_micro_topics) > MAX_TOPICS_PER_REDUCE:
            print(f"[PIPELINE] 🗂️ Topic count exceeds safe Groq limit. Running Hierarchical Sub-Reduces...")
            intermediate_topics = []
            
            # Batch the micro-topics into safe sizes
            for i in range(0, len(all_micro_topics), MAX_TOPICS_PER_REDUCE):
                batch = all_micro_topics[i : i + MAX_TOPICS_PER_REDUCE]
                print(f"[PIPELINE] ⏳ Sub-Reducing topics {i+1} to {min(i+MAX_TOPICS_PER_REDUCE, len(all_micro_topics))}...")
                
                micro_topics_text = "\n".join([f"- {t.title}: {t.summary}" for t in batch])
                sub_result: TopicList = await self.reduce_chain.ainvoke({"transcript": f"Consolidate these micro-topics into a logical curriculum:\n{micro_topics_text}"})
                
                if sub_result and sub_result.topics:
                    # Keep the top consolidated topics to avoid bloat
                    intermediate_topics.extend(sub_result.topics[:5])
                    
                # TPM Cooldown between sub-reduces
                if i + MAX_TOPICS_PER_REDUCE < len(all_micro_topics):
                    print("[PIPELINE] ⏱️ TPM Cooldown: Sleeping 15 seconds before next Sub-Reduce...")
                    await asyncio.sleep(15)
                    
            all_micro_topics = intermediate_topics
            print(f"[PIPELINE] 🔄 Running Final Reduce on {len(all_micro_topics)} consolidated topics...")

        # 5. Final Reduce Phase
        micro_topics_text = "\n".join([f"- {t.title}: {t.summary}" for t in all_micro_topics])
        final_result: TopicList = await self.reduce_chain.ainvoke({"transcript": f"Consolidate these micro-topics into a logical curriculum:\n{micro_topics_text}"})
        
        return final_result

