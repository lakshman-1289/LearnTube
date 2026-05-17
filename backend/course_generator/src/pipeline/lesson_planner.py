from models.pipeline_schemas import LessonPlan, TopicList
from course_generator.src.core.langchain_utils import get_json_llm
from course_generator.src.pipeline.prompts import Prompts

class LessonPlanner:
    def __init__(self, llm=None):
        self.llm = llm or get_json_llm()
        self.chain = (Prompts.LESSON_PLANNER | self.llm.with_structured_output(LessonPlan, method="json_mode")).with_retry(stop_after_attempt=3)

    async def plan_lessons(self, topics: TopicList, min_lessons: int = 1, max_lessons: int = 6) -> LessonPlan:
        """
        Plans lessons from an extracted topic list.
        Enforces min/max lesson count based on transcript length.
        Uses LangChain LCEL.
        """
        # For large topic lists, evenly sample to keep the prompt within LLM context.
        MAX_TOPICS = 80
        sampled_topics = topics
        if len(topics.topics) > MAX_TOPICS:
            step = max(1, len(topics.topics) // MAX_TOPICS)
            sampled = topics.topics[::step][:MAX_TOPICS]
            sampled_topics = TopicList(topics=sampled)
            print(f"[LESSON_PLANNER] Sampled {len(sampled_topics.topics)} representative topics from {len(topics.topics)} total.")

        topics_json = sampled_topics.model_dump_json(indent=2)
        
        # LCEL execution
        result: LessonPlan = await self.chain.ainvoke({
            "topics_json": topics_json,
            "min_lessons": min_lessons,
            "max_lessons": max_lessons
        })
        
        # Clamp lesson count to the target range post-generation just in case
        if len(result.lessons) > max_lessons:
            print(f"[LESSON_PLANNER] Clamping {len(result.lessons)} → {max_lessons} lessons")
            result.lessons = result.lessons[:max_lessons]
        elif len(result.lessons) < min_lessons and result.lessons:
            print(f"[LESSON_PLANNER] Warning: only {len(result.lessons)} lessons generated (min={min_lessons})")

        return result
