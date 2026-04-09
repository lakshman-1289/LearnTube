from models.pipeline_schemas import LessonContent
from course_generator.src.core.groq_client import GroqClient
import os
from course_generator.src.pipeline.prompts import Prompts
from course_generator.src.pipeline.safe_pipeline import (
    smart_chunk_text,
    summarize_chunks,
    count_tokens,
)
from course_generator.src.services.groq_service import safe_groq_request
from course_generator.src.core.llm_utils import clean_llm_json, normalize_lesson
from pydantic import ValidationError
import json


class ContentGenerator:
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client

    async def generate_lesson_content(self, lesson_title: str, lesson_subtitle: str, transcript_context: str) -> LessonContent:
        """
        Two-stage generation:
        1) Token-aware chunking + summarization (reduce transcript to concise summary chunks)
        2) Generate lesson content from the combined summaries using a compact prompt

        This ensures we never send >8000 tokens per request and keeps semantic integrity.
        """

        # 1) Chunk transcript strictly by tokens (safe limit 2000; reserve room for summary output)
        prompt_template = "Summarize the transcript chunk:\n{transcript}\n"
        chunks = smart_chunk_text(
            transcript_context,
            prompt_template=prompt_template,
            max_input_tokens=2000,
            max_output_tokens=300,
            buffer_tokens=50,
        )

        # 2) Summarize each chunk (cached)
        summaries = await summarize_chunks(self.client, chunks, summary_max_tokens=300)

        # Combine summaries into a single short context (still small)
        combined_summary = "\n\n".join(summaries)
        print(f"[CONTENT_GEN] Combined summary tokens={count_tokens(combined_summary)} chars={len(combined_summary)}")

        # 3) Build a strict prompt that enforces exact JSON schema and forbids extra text/markdown
        schema_snippet = (
            '{\n'
            '  "lessonTitle": "string",\n'
            '  "introduction": "string",\n'
            '  "sections": [\n'
            '    {"title": "string", "type": "string", "points": ["string"] }\n'
            '  ],\n'
            '  "conclusion": "string"\n'
            '}'
        )

        strict_prompt = (
            "You are an expert educational content writer.\n"
            "Produce EXACTLY and ONLY a JSON object that matches the schema below.\n"
            "Do NOT include any markdown, explanation, or extra fields. Return raw JSON only.\n"
            "Do NOT include trailing commas. Do NOT wrap JSON in code fences.\n"
            "Follow the schema EXACTLY. If any field is missing, return an empty string or empty list (do not omit keys).\n\n"
            "SCHEMA:\n" + schema_snippet + "\n\n"
            "GROUND TRUTH (use only this summary; do NOT hallucinate):\n" + combined_summary + "\n\n"
            f"Context fields you can use:\n- lessonTitle: {lesson_title}\n- lessonSubtitle (do NOT include this field in the output schema)\n\n"
            "Return ONLY valid JSON matching the schema exactly."
        )

        # We removed the LLM retries; we just coerce it on the backend.
        json_text = await safe_groq_request(
            prompt=strict_prompt,
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            max_tokens=900,
            temperature=0.2,
            token_limit=2500,
            stage_context=f"generate_lesson_{lesson_title}",
        )

        try:
            parsed = clean_llm_json(json_text)
        except Exception as e:
            print(f"⚠️ [CONTENT_GEN] Failed to extract JSON: {e}")
            parsed = {}

        # The super-strict normalizer forces the parsed dict into the Pydantic schema shape implicitly
        normalized = normalize_lesson(parsed)
        print(f"📊 [CONTENT_GEN] Normalized JSON preview: {str(normalized)[:300]}")
        
        try:
            validated = LessonContent(**normalized)
            # Content quality validation
            if not self._is_valid_content(validated):
                print(f"⚠️ [CONTENT_GEN] Low-quality content detected. Retrying once...")
                return await self._retry_generate_lesson_content(lesson_title, lesson_subtitle, strict_prompt)
            print(f"✅ [CONTENT_GEN] Success. Lesson Content validated.")
            return validated
        except ValidationError as ve:
            raise RuntimeError(f"Validation inherently failed despite normalization: {ve}\nNORMD: {normalized}")

    def _is_valid_content(self, content: LessonContent) -> bool:
        """Validates lesson content meets minimum quality standards."""
        # Introduction must have at least 50 chars (roughly 2-3 sentences)
        if not content.introduction or len(content.introduction.strip()) < 50:
            print(f"⚠️ [CONTENT_GEN] Invalid: introduction too short ({len(content.introduction.strip()) if content.introduction else 0} chars)")
            return False
        # Must have at least 2 sections
        if len(content.sections) < 2:
            print(f"⚠️ [CONTENT_GEN] Invalid: only {len(content.sections)} section(s)")
            return False
        # Each section must have at least 2 points
        for i, section in enumerate(content.sections):
            if len(section.points) < 2:
                print(f"⚠️ [CONTENT_GEN] Invalid: section {i} has only {len(section.points)} point(s)")
                return False
        return True

    async def _retry_generate_lesson_content(self, lesson_title: str, lesson_subtitle: str, original_prompt: str) -> LessonContent:
        """Single retry with a reinforced prompt."""
        retry_prompt = (
            "IMPORTANT: The previous response was rejected for low quality.\n"
            "You MUST include:\n"
            "- introduction: at least 2 full sentences\n"
            "- at least 2 sections\n"
            "- at least 2 points per section\n\n"
        ) + original_prompt

        json_text = await safe_groq_request(
            prompt=retry_prompt,
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            max_tokens=900,
            temperature=0.3,
            token_limit=2500,
            stage_context=f"retry_lesson_{lesson_title}",
        )
        try:
            parsed = clean_llm_json(json_text)
        except Exception:
            parsed = {}
        normalized = normalize_lesson(parsed)
        try:
            return LessonContent(**normalized)
        except ValidationError as ve:
            raise RuntimeError(f"Retry also failed validation: {ve}")
