from models.pipeline_schemas import LessonContent
from course_generator.src.core.langchain_utils import get_json_llm
from course_generator.src.pipeline.prompts import Prompts
from langchain_core.runnables import RunnablePassthrough

class ContentGenerator:
    def __init__(self, llm=None):
        self.llm = llm or get_json_llm(model_name="llama-3.1-8b-instant", temperature=0.2)
        # The chain expects {lesson_title, lesson_subtitle, transcript_segment}
        self.chain = (Prompts.CONTENT_GENERATOR | self.llm.with_structured_output(LessonContent, method="json_mode")).with_retry(stop_after_attempt=3)

    async def generate_lesson_content(self, lesson_title: str, lesson_subtitle: str, retriever) -> LessonContent:
        """
        Uses RAG to fetch the most relevant transcript chunks for the given lesson title,
        then uses an LCEL chain to generate structured lesson content.
        """
        print(f"[CONTENT_GEN] Fetching relevant chunks for: {lesson_title}...")
        
        # 1. Retrieve relevant documents using the lesson title as the query
        docs = retriever.invoke(lesson_title)
        
        # 2. Combine the retrieved chunks into a single context string
        combined_context = "\n\n".join([doc.page_content for doc in docs])
        print(f"[CONTENT_GEN] Retrieved {len(docs)} chunks. Context length: {len(combined_context)} chars.")

        # 3. Generate structured content via LCEL
        result: LessonContent = await self.chain.ainvoke({
            "lesson_title": lesson_title,
            "lesson_subtitle": lesson_subtitle,
            "transcript_segment": combined_context
        })
        
        # 4. Light validation (fallback/retry omitted for brevity, Pydantic handles structural validation natively)
        print(f"✅ [CONTENT_GEN] Success. Lesson Content generated for '{lesson_title}'.")
        return result
