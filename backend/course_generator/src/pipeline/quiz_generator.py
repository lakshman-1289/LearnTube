from models.pipeline_schemas import LessonContent, QuizList
from course_generator.src.core.langchain_utils import get_json_llm
from course_generator.src.pipeline.prompts import Prompts

class QuizGenerator:
    def __init__(self, llm=None):
        self.llm = llm or get_json_llm()
        self.chain = (Prompts.QUIZ_GENERATOR | self.llm.with_structured_output(QuizList, method="json_mode")).with_retry(stop_after_attempt=3)

    async def generate_quizzes(self, lesson_content: LessonContent) -> QuizList:
        """
        Agent to construct precise quizzes from generated educational content.
        Uses LangChain LCEL.
        """
        result: QuizList = await self.chain.ainvoke({
            "lesson_content": lesson_content.model_dump_json()
        })
        
        # Python-side coercion to explicitly satisfy UI defaults just in case
        # (Though Pydantic OutputParser usually handles this well, we add IDs to ensure UI works)
        for i, q in enumerate(result.quizzes):
            q.id = i + 1
            if not q.type:
                q.type = "multiple_choice"
            
            # ensure exactly 4 parameters
            while len(q.options) < 4: 
                q.options.append(f"Option {len(q.options)+1}")
            q.options = q.options[:4]
            
            # coerce correct answers
            ca = q.correctAnswer
            if ca < 0 or ca > 3: 
                ca = 0
            q.correctAnswer = ca
            
            if not q.answer:
                q.answer = q.options[ca]
        
        return result
