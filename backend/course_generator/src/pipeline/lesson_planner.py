import json
from models.pipeline_schemas import LessonPlan, TopicList
from course_generator.src.core.groq_client import GroqClient
from course_generator.src.pipeline.prompts import Prompts

class LessonPlanner:
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client

    async def plan_lessons(self, topics: TopicList, min_lessons: int = 1, max_lessons: int = 6) -> LessonPlan:
        """
        Plans lessons from an extracted topic list.
        Enforces min/max lesson count based on transcript length.
        """
        # For large topic lists, evenly sample to keep the prompt within LLM context.
        # Sending hundreds of raw topics causes auto-truncation and produces only 1 lesson.
        MAX_TOPICS = 80
        sampled_topics = topics
        if len(topics.topics) > MAX_TOPICS:
            step = max(1, len(topics.topics) // MAX_TOPICS)
            sampled = topics.topics[::step][:MAX_TOPICS]
            sampled_topics = TopicList(topics=sampled)
            print(f"[LESSON_PLANNER] Sampled {len(sampled_topics.topics)} representative topics from {len(topics.topics)} total.")

        topics_json = sampled_topics.model_dump_json(indent=2)
        prompt = Prompts.LESSON_PLANNER.format(
            topics_json=topics_json,
            min_lessons=min_lessons,
            max_lessons=max_lessons,
        )

        messages = [{"role": "user", "content": prompt}]

        schema_snippet = (
            '{\n'
            '  "lessons": [\n'
            '    {\n'
            '      "title": "string",\n'
            '      "subtitle": "string",\n'
            '      "videoMeta": {"start": "00:00:00", "end": "00:05:00"}\n'
            '    }\n'
            '  ]\n'
            '}'
        )

        messages.append({"role": "system", "content": f"Return ONLY valid JSON exactly matching this schema:\n{schema_snippet}\nDo NOT output raw schemas or markdown."})

        # max_tokens must be large enough to output all lesson entries (each entry ~80 tokens)
        output_budget = max(1500, max_lessons * 100)
        raw_json_str = await self.client.chat_completion(
            messages=messages,
            max_tokens=output_budget,
            temperature=0.3, # slightly higher for creativity on titles
            response_format={"type": "json_object"},
            model="llama-3.1-8b-instant"
        )
        
        from course_generator.src.core.llm_utils import clean_llm_json
        try: parsed = clean_llm_json(raw_json_str)
        except Exception: parsed = {}
        
        if "lessons" not in parsed:
            if isinstance(parsed, list): parsed = {"lessons": parsed}
            else: parsed = {"lessons": [parsed]}
            
        for l in parsed.get("lessons", []):
            if not isinstance(l, dict): continue
            if "title" not in l: l["title"] = "Lesson Section"
            if "subtitle" not in l: l["subtitle"] = "Core Concepts"
            if "videoMeta" not in l or not isinstance(l["videoMeta"], dict):
                l["videoMeta"] = {"start": "00:00:00", "end": "00:00:00"}
            else:
                vm = l["videoMeta"]
                if "start_time" in vm and "start" not in vm:
                    vm["start"] = vm.pop("start_time")
                if "end_time" in vm and "end" not in vm:
                    vm["end"] = vm.pop("end_time")
                
        # Clamp lesson count to the target range
        lessons = parsed.get("lessons", [])
        if len(lessons) > max_lessons:
            print(f"[LESSON_PLANNER] Clamping {len(lessons)} → {max_lessons} lessons")
            parsed["lessons"] = lessons[:max_lessons]
        elif len(lessons) < min_lessons and lessons:
            print(f"[LESSON_PLANNER] Warning: only {len(lessons)} lessons generated (min={min_lessons})")

        result = LessonPlan(**parsed)
        return result
