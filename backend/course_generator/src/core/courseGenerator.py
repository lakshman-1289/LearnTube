from typing import Dict, Tuple
from course_generator.src.core.langchain_utils import get_json_llm, build_transcript_retriever
from course_generator.src.pipeline.topic_extractor import TopicExtractor
from course_generator.src.pipeline.lesson_planner import LessonPlanner
from course_generator.src.pipeline.content_generator import ContentGenerator
from course_generator.src.pipeline.quiz_generator import QuizGenerator
from course_generator.src.pipeline.course_assembler import CourseAssembler
from models.pipeline_schemas import FinalCourse
import asyncio

class CourseGenerator:
    """
    Acts as the Orchestrator for the entire course generation pipeline.
    Uses LangChain abstractions (Retrievers, LCEL) where applicable.
    """
    def __init__(self, groq_client=None):
        # We keep the param for backward compatibility in routers, but ignore it.
        # Initialize LangChain LLM
        self.llm = get_json_llm()

        # Initialize specialized LCEL agents
        self.topic_extractor = TopicExtractor(self.llm)
        self.lesson_planner = LessonPlanner(self.llm)
        self.content_generator = ContentGenerator(self.llm)
        self.quiz_generator = QuizGenerator(self.llm)

    @staticmethod
    def _get_target_lesson_range(transcript_text: str) -> Tuple[int, int]:
        word_count = len(transcript_text.split())
        print(f"[PIPELINE] 📏 Transcript word count: {word_count}")
        if word_count < 2_000:
            return 1, 3
        elif word_count < 6_000:
            return 3, 6
        elif word_count < 20_000:
            return 6, 10
        elif word_count < 60_000:
            return 10, 15
        else:
            return 15, 20

    async def generate_complete_course(self, transcript_text: str, video_title: str, video_url: str = "original_video_url") -> Dict:
        """
        Coordinates the pipeline execution using LangChain Retrievers and LCEL components.
        """
        try:
            min_lessons, max_lessons = self._get_target_lesson_range(transcript_text)
            print(f"[PIPELINE] 🎯 Target lesson range: {min_lessons}–{max_lessons}")

            print("[PIPELINE] 🚀 Starting Topic Extraction...")
            topics = await self.topic_extractor.extract_topics(transcript_text)
            print(f"[PIPELINE] ✅ Extracted {len(topics.topics)} topics.")

            print("[PIPELINE] 🗓️ Planning Lessons...")
            lesson_plan = await self.lesson_planner.plan_lessons(topics, min_lessons=min_lessons, max_lessons=max_lessons)
            print(f"[PIPELINE] ✅ Planned {len(lesson_plan.lessons)} lessons.")
            
            # --- LANGCHAIN RAG INTEGRATION ---
            print("[PIPELINE] 📚 Building Document Retriever for RAG...")
            retriever = build_transcript_retriever(transcript_text)
            
            lesson_contents = []
            lesson_quizzes = []

            # Process contents and quizzes. 
            # We iterate sequentially to respect Groq free tier limit of 12000 TPM
            # LangChain LCEL supports .batch(), but we use sequential to inject sleep.
            for i, lesson_outline in enumerate(lesson_plan.lessons):
                print(f"[PIPELINE] 📖 Generating content for Lesson {i+1}/{len(lesson_plan.lessons)}: {lesson_outline.title}")
                
                # Fetch context and generate content via LCEL + Retriever
                content = await self.content_generator.generate_lesson_content(
                    lesson_title=lesson_outline.title,
                    lesson_subtitle=lesson_outline.subtitle,
                    retriever=retriever
                )
                lesson_contents.append(content)
                
                print(f"[PIPELINE] 🧠 Generating quizzes for Lesson {i+1}")
                quizzes = await self.quiz_generator.generate_quizzes(content)
                lesson_quizzes.append(quizzes)
                
                if i < len(lesson_plan.lessons) - 1:
                    print("[PIPELINE] ⏱️ Sleeping 15s to keep Groq TPM boundaries safe...")
                    await asyncio.sleep(15)

            print("[PIPELINE] 🏗️ Assembling Final Course JSON...")
            final_course: FinalCourse = CourseAssembler.assemble_final_course(
                video_url=video_url,
                video_title=video_title,
                lesson_outlines=lesson_plan.lessons,
                lesson_contents=lesson_contents,
                lesson_quizzes=lesson_quizzes
            )

            print("[PIPELINE] 🎉 Success! Returning Pydantic validated course data.")
            return final_course.model_dump()

        except Exception as e:
            print(f"[PIPELINE ERROR] ❌ Generation failed at pipeline stage: {str(e)}")
            return {"error": str(e)}