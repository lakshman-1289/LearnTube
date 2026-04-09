class Prompts:
    TOPIC_EXTRACTION = """
You are an expert course architect.

### 🎯 Goal
Analyze the provided transcript and extract a logically ordered list of main topics covered.

### ⚠️ Rules
1. Topics must be distinct and sequential based on the transcript.
2. Provide a short summary of each topic.
3. Extract accurate start and end timestamps (if provided in transcript structure, else approximate relative flow).
4. Output MUST be strictly JSON mapping to the requested schema.

### 📦 Transcript:
{transcript}
"""

    LESSON_PLANNER = """
You are an expert curriculum designer.

### 🎯 Goal
Convert the following extracted topics into structured lesson plans.

### ⚠️ Rules
1. Create a clear, engaging title and subtitle for each lesson.
2. IMPORTANT: Generate BETWEEN {min_lessons} and {max_lessons} lessons ONLY. Merge or group topics if needed.
3. Do not generate the actual content yet, just the outline mapping the `title`, `subtitle`, and `videoMeta`.
4. Return strictly valid JSON formatted to the `LessonPlan` schema.

### 📦 Topics:
{topics_json}
"""

    CONTENT_GENERATOR = """
You are an expert educational content writer.

### 🎯 Goal
Generate detailed, comprehensive, and engaging lesson content for the topic: "{lesson_title}".

### ⚠️ Rules
1. Use the provided transcript segment as ground truth. Do not hallucinate outside facts.
2. Structure the content strictly into:
   - introduction: 2–3 full sentences explaining what the lesson covers
   - sections: AT LEAST 2 sections mixing 'concept' and 'example' types
   - conclusion: Short 1–2 sentence summary
3. Each section MUST have AT LEAST 2 points with subtitles and detailed explanations (min 1 sentence each).
4. If a concept is abstract, follow it with an 'example' section with real-world context.
5. All text MUST be in CLEAR ENGLISH regardless of original language.
6. NEVER produce empty introduction, sections, or points. Always provide substantive content.
7. Return strictly valid JSON formatted to the `LessonContent` schema.

### 📦 Topic Context:
Lesson Subtitle: {lesson_subtitle}

### 📦 Source Transcript Segment:
{transcript_segment}
"""

    QUIZ_GENERATOR = """
You are an expert educational evaluator.

### 🎯 Goal
Generate exactly 3 multiple-choice questions to test understanding of the lesson content below.

### ⚠️ Rules
1. Generate EXACTLY 3 questions — no more, no less.
2. Mix types: Q1 = conceptual (why/how), Q2 = scenario-based application, Q3 = tricky/common-misconception.
3. Each question MUST have EXACTLY 4 answer options (no duplicates).
4. `correctAnswer` MUST be an integer index 0–3 matching the correct option.
5. `answer` MUST be the exact text of the correct option string.
6. `explanation` must clearly explain why the answer is correct and why the others are wrong.
7. All questions must be answerable from the lesson content alone.
8. Return ONLY valid JSON, no markdown, no extra text.

### 📦 Lesson Content:
{lesson_content}
"""

