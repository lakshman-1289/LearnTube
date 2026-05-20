from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models.pipeline_schemas import TopicList, LessonPlan, LessonContent, QuizList

topic_parser = PydanticOutputParser(pydantic_object=TopicList)
lesson_plan_parser = PydanticOutputParser(pydantic_object=LessonPlan)
content_parser = PydanticOutputParser(pydantic_object=LessonContent)
quiz_parser = PydanticOutputParser(pydantic_object=QuizList)

class Prompts:
    MAP_TOPIC_EXTRACTION = ChatPromptTemplate.from_messages([
        ("system", "You are an expert content analyzer.\n\n"
                   "Extract a MAXIMUM of 3 most critical micro-topics from the provided transcript segment.\n"
                   "Output exactly a JSON object mapping to the requested schema. DO NOT wrap the JSON in markdown blocks (```json) or `<function>` tags.\n"
                   "{format_instructions}"),
        ("human", "### 📦 Transcript Segment:\n{transcript}")
    ]).partial(format_instructions=topic_parser.get_format_instructions())

    TOPIC_EXTRACTION = ChatPromptTemplate.from_messages([
        ("system", "You are an expert course architect.\n\n"
                   "### 🎯 Goal\n"
                   "Analyze the provided transcript or micro-topics and extract a logically ordered list of main topics covered.\n\n"
                   "### ⚠️ Rules\n"
                   "1. Topics must be distinct and sequential based on the transcript.\n"
                   "2. Provide a short summary of each topic.\n"
                   "3. Extract accurate start and end timestamps (if provided in transcript structure, else approximate relative flow).\n"
                   "4. Output MUST be strictly JSON mapping to the requested schema.\n\n"
                   "### 🛑 CRITICAL INSTRUCTION\n"
                   "DO NOT output the JSON schema definition. ONLY output the final populated JSON object containing your actual extracted topics. Do not include any explanations.\n\n"
                   "{format_instructions}"),
        ("human", "### 📦 Content:\n{transcript}")
    ]).partial(format_instructions=topic_parser.get_format_instructions())

    LESSON_PLANNER = ChatPromptTemplate.from_messages([
        ("system", "You are an expert curriculum designer.\n\n"
                   "### 🎯 Goal\n"
                   "Convert the following extracted topics into structured lesson plans.\n\n"
                   "### ⚠️ Rules\n"
                   "1. Create a clear, engaging title and subtitle for each lesson.\n"
                   "2. IMPORTANT: Generate BETWEEN {min_lessons} and {max_lessons} lessons ONLY. Merge or group topics if needed.\n"
                   "3. Do not generate the actual content yet, just the outline mapping the `title`, `subtitle`, and `videoMeta`.\n"
                   "4. Return strictly valid JSON formatted to the `LessonPlan` schema.\n\n"
                   "### 🛑 CRITICAL INSTRUCTION\n"
                   "DO NOT output the JSON schema definition. ONLY output the final populated JSON object containing your actual generated lesson plans. Do not include any explanations.\n"
                   "IMPORTANT: Your output MUST be a JSON object with a single root key called `lessons` which contains the array of lesson objects. Do NOT output a raw JSON array.\n\n"
                   "{format_instructions}"),
        ("human", "### 📦 Topics:\n{topics_json}")
    ]).partial(format_instructions=lesson_plan_parser.get_format_instructions())

    CONTENT_GENERATOR = ChatPromptTemplate.from_messages([
        ("system", "You are an expert educational content writer.\n\n"
                   "### 🎯 Goal\n"
                   "Generate detailed, comprehensive, and engaging lesson content for the topic: \"{lesson_title}\".\n\n"
                   "### ⚠️ Rules\n"
                   "1. Use the provided transcript segment as ground truth. Do not hallucinate outside facts.\n"
                   "2. Structure the content strictly into:\n"
                   "   - introduction: 2–3 full sentences explaining what the lesson covers\n"
                   "   - sections: AT LEAST 2 sections mixing 'concept' and 'example' types\n"
                   "   - conclusion: Short 1–2 sentence summary\n"
                   "3. Each section MUST have AT LEAST 2 points with subtitles and detailed explanations (min 1 sentence each).\n"
                   "4. If a concept is abstract, follow it with an 'example' section with real-world context.\n"
                   "5. All text MUST be in CLEAR ENGLISH regardless of original language.\n"
                   "6. NEVER produce empty introduction, sections, or points. Always provide substantive content.\n"
                   "7. Return strictly valid JSON formatted to the `LessonContent` schema.\n\n"
                   "### 🛑 CRITICAL INSTRUCTION\n"
                   "DO NOT output the JSON schema definition. ONLY output the final populated JSON object containing your actual generated lesson content. Do not include any explanations.\n\n"
                   "{format_instructions}"),
        ("human", "### 📦 Topic Context:\nLesson Subtitle: {lesson_subtitle}\n\n### 📦 Source Transcript Segment:\n{transcript_segment}")
    ]).partial(format_instructions=content_parser.get_format_instructions())

    QUIZ_GENERATOR = ChatPromptTemplate.from_messages([
        ("system", "You are an expert educational evaluator.\n\n"
                   "### 🎯 Goal\n"
                   "Generate exactly 3 multiple-choice questions to test understanding of the lesson content below.\n\n"
                   "### ⚠️ Rules\n"
                   "1. Generate EXACTLY 3 questions — no more, no less.\n"
                   "2. Mix types: Q1 = conceptual (why/how), Q2 = scenario-based application, Q3 = tricky/common-misconception.\n"
                   "3. Each question MUST have EXACTLY 4 answer options (no duplicates).\n"
                   "4. `correctAnswer` MUST be an integer index 0–3 matching the correct option.\n"
                   "5. `answer` MUST be the exact text of the correct option string.\n"
                   "6. `explanation` must clearly explain why the answer is correct and why the others are wrong.\n"
                   "7. All questions must be answerable from the lesson content alone.\n"
                   "8. Return ONLY valid JSON, no markdown, no extra text.\n\n"
                   "### 🛑 CRITICAL INSTRUCTION\n"
                   "DO NOT output the JSON schema definition. ONLY output the final populated JSON object containing your actual generated quizzes. Do not include any explanations.\n\n"
                   "{format_instructions}"),
        ("human", "### 📦 Lesson Content:\n{lesson_content}")
    ]).partial(format_instructions=quiz_parser.get_format_instructions())

