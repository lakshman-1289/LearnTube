import operator
from typing import Annotated, TypedDict, List, Dict, Any, Optional
import asyncio

from langgraph.graph import StateGraph, START, END

from course_generator.src.pipeline.topic_extractor import TopicExtractor
from course_generator.src.pipeline.lesson_planner import LessonPlanner
from course_generator.src.pipeline.content_generator import ContentGenerator
from course_generator.src.pipeline.quiz_generator import QuizGenerator
from course_generator.src.core.langchain_utils import build_transcript_retriever, chunk_transcript_for_rag
from course_generator.src.pipeline.course_assembler import CourseAssembler
from models.pipeline_schemas import TopicList, LessonPlan, LessonContent, QuizList, FinalCourse

class CourseState(TypedDict):
    """State object for the LangGraph orchestrator."""
    transcript_text: str
    video_title: str
    video_url: str
    min_lessons: int
    max_lessons: int
    
    # Internal Pipeline State
    chunks: List[str]
    retriever: Any
    topics: TopicList
    lesson_plan: LessonPlan
    
    # Results
    lesson_contents: List[LessonContent]
    lesson_quizzes: List[QuizList]
    
    final_course: Dict[str, Any]
    error: Optional[str]


async def node_extract_topics(state: CourseState):
    """Maps chunks to topics, then reduces to a curriculum."""
    print("[GRAPH] 🏃 Node: extract_topics")
    extractor = TopicExtractor()
    topics = await extractor.extract_topics(state["transcript_text"])
    chunks = chunk_transcript_for_rag(state["transcript_text"])
    return {"topics": topics, "chunks": chunks}


async def node_plan_lessons(state: CourseState):
    """Plans lessons from topics."""
    print("[GRAPH] 🏃 Node: plan_lessons")
    planner = LessonPlanner()
    lesson_plan = await planner.plan_lessons(state["topics"], state["min_lessons"], state["max_lessons"])
    return {"lesson_plan": lesson_plan}


async def node_build_retriever(state: CourseState):
    """Builds the MMR retriever from chunks."""
    print("[GRAPH] 🏃 Node: build_retriever")
    retriever = build_transcript_retriever(state["chunks"])
    return {"retriever": retriever}


async def node_generate_all_content(state: CourseState):
    """Generates content and quizzes using a Production Bounded Async Worker Queue."""
    import asyncio
    from course_generator.src.core.llm_provider.factory import LLMFactory
    from course_generator.src.core.llm_provider.interfaces import ProviderType
    
    print("[GRAPH] 🏃 Node: generate_all_content (Worker Queue Strategy)")
    content_gen = ContentGenerator()
    quiz_gen = QuizGenerator()
    retriever = state["retriever"]
    
    # 1. Initialize the Task Queue
    queue = asyncio.Queue()
    
    # 2. Maintain a list to store results in the correct order
    # Queue processing is unordered, so we store results in a pre-allocated array by index
    num_lessons = len(state["lesson_plan"].lessons)
    results = [None] * num_lessons
    
    # Push all tasks into the queue with their original index
    for index, outline in enumerate(state["lesson_plan"].lessons):
        queue.put_nowait((index, outline))
        
    async def with_exponential_backoff(coro_func, *args, max_retries=3, base_delay=15):
        """Internal helper for intercepting LLM rate limits and backing off safely."""
        for attempt in range(max_retries + 1):
            try:
                return await coro_func(*args)
            except Exception as e:
                error_str = str(e).lower()
                if attempt < max_retries and ("429" in error_str or "rate_limit" in error_str or "tpm" in error_str or "503" in error_str):
                    delay = base_delay * (2 ** attempt)
                    print(f"[RETRY] ⚠️ LLM Rate limit hit. Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise e
                    
    async def worker(worker_id: int):
        print(f"[WORKER-{worker_id}] 🟢 Started.")
        while True:
            try:
                # Pop task from queue
                index, outline = await queue.get()
                print(f"[WORKER-{worker_id}] 📖 Processing Lesson: {outline.title}")
                
                try:
                    # Execute with robust exponential backoff
                    content = await with_exponential_backoff(content_gen.generate_lesson_content, outline.title, outline.subtitle, retriever)
                    print(f"[WORKER-{worker_id}] 🧠 Generating quizzes for: {outline.title}")
                    quizzes = await with_exponential_backoff(quiz_gen.generate_quizzes, content)
                    
                    results[index] = (content, quizzes)
                except Exception as e:
                    print(f"[WORKER-{worker_id}] ❌ Permanent failure on lesson '{outline.title}': {e}")
                    # Fault Isolation: Generate empty fallback objects to prevent entire pipeline crash
                    from models.pipeline_schemas import LessonContent, QuizList
                    results[index] = (
                        LessonContent(introduction="Content generation failed.", sections=[], conclusion=""),
                        QuizList(quizzes=[])
                    )
                finally:
                    # MUST call task_done or queue.join() blocks forever
                    queue.task_done()
                    
                    # Adaptive Cooldown: Token-aware backpressure release valve
                    provider = LLMFactory.get_provider()
                    cooldown = 15 if provider == ProviderType.GROQ else 2
                    print(f"[WORKER-{worker_id}] ⏱️ Cooldown for {cooldown}s before pulling next task...")
                    await asyncio.sleep(cooldown)
                    
            except asyncio.CancelledError:
                print(f"[WORKER-{worker_id}] 🔴 Cancelled via Orchestrator shutdown.")
                break
            except Exception as e:
                print(f"[WORKER-{worker_id}] 💥 Unexpected worker crash: {e}")
                # Ensure queue unblocks even if worker fatally crashes
                queue.task_done()

    # 3. Spawn a bounded worker pool based on provider limits
    provider = LLMFactory.get_provider()
    # If Groq free tier, restrict to exactly 1 sequential worker to absolutely prevent TPM overlap
    num_workers = 1 if provider == ProviderType.GROQ else 3
    print(f"[GRAPH] ⚙️ Spawning {num_workers} background workers for Queue Orchestration...")
    
    workers = [asyncio.create_task(worker(i)) for i in range(num_workers)]
    
    # 4. Await queue completion (Queue acts as the synchronization primitive)
    print(f"[GRAPH] ⏳ Waiting for {num_lessons} tasks to be processed...")
    await queue.join()
    print("[GRAPH] ✅ Queue processing complete. Shutting down workers.")
    
    # 5. Clean Lifecycle: explicitly cancel infinite-loop workers to free event loop resources
    for w in workers:
        w.cancel()
        
    await asyncio.gather(*workers, return_exceptions=True)
    
    # 6. Extract sequential results safely
    contents = [r[0] for r in results]
    quizzes = [r[1] for r in results]
    
    return {
        "lesson_contents": contents,
        "lesson_quizzes": quizzes
    }


async def node_assemble_course(state: CourseState):
    """Assembles the final validated Pydantic model into JSON."""
    print("[GRAPH] 🏃 Node: assemble_course")
    final_course = CourseAssembler.assemble_final_course(
        video_url=state["video_url"],
        video_title=state["video_title"],
        lesson_outlines=state["lesson_plan"].lessons,
        lesson_contents=state["lesson_contents"],
        lesson_quizzes=state["lesson_quizzes"]
    )
    return {"final_course": final_course.model_dump()}


def build_course_graph():
    """Compiles the LangGraph DAG workflow."""
    builder = StateGraph(CourseState)
    
    builder.add_node("extract_topics", node_extract_topics)
    builder.add_node("plan_lessons", node_plan_lessons)
    builder.add_node("build_retriever", node_build_retriever)
    builder.add_node("generate_all_content", node_generate_all_content)
    builder.add_node("assemble_course", node_assemble_course)
    
    # Flow definition
    builder.add_edge(START, "extract_topics")
    builder.add_edge("extract_topics", "plan_lessons")
    builder.add_edge("plan_lessons", "build_retriever")
    builder.add_edge("build_retriever", "generate_all_content")
    builder.add_edge("generate_all_content", "assemble_course")
    builder.add_edge("assemble_course", END)
    
    return builder.compile()
