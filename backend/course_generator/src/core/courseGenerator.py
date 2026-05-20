from typing import Dict, Tuple
from course_generator.src.agents.course_graph import build_course_graph
import asyncio

class CourseGenerator:
    """
    Acts as the Orchestrator for the entire course generation pipeline.
    Now utilizes LangGraph for Agentic stateful execution.
    """
    def __init__(self):
        self.graph = build_course_graph()

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
        Coordinates the pipeline execution using LangGraph.
        """
        try:
            min_lessons, max_lessons = self._get_target_lesson_range(transcript_text)
            
            # Initialize State
            initial_state = {
                "transcript_text": transcript_text,
                "video_title": video_title,
                "video_url": video_url,
                "min_lessons": min_lessons,
                "max_lessons": max_lessons,
            }
            
            # Execute LangGraph Workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            print("[PIPELINE] 🎉 Success! Returning Pydantic validated course data.")
            return final_state["final_course"]

        except Exception as e:
            print(f"[PIPELINE ERROR] ❌ Generation failed at pipeline stage: {str(e)}")
            return {"error": str(e)}