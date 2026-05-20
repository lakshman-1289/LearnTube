"""
content_classifier.py
Classifies video content as 'educational', 'entertainment', or 'other'
using keyword pre-filtering + LLM fallback.
"""

import os
import re
import json
import aiohttp

# Keywords that immediately identify non-educational content
_ENTERTAINMENT_KEYWORDS = [
    # Movie/TV scenes (any "X scene" pattern)
    "movie scene", "film scene", "movie clip", "film clip",
    "hit scene", "super hit", "best scene", "climax scene",
    "action scene", "fight scene", "love scene", "comedy scene",
    "interval scene", "blockbuster scene", "mass scene",
    "award winning scene", "power packed",
    # Trailers / promos
    "trailer", "movie trailer", "official trailer", "teaser", "short film",
    # Music
    "official video", "music video", "lyric video", "audio song",
    "full song", "video song", "album", "single",
    # Comedy / Entertainment
    "stand-up", "standup", "comedy show", "funny video", "prank",
    "reaction video", "roast",
    # Sports / Gaming
    "highlights", "match highlights", "gameplay", "gaming stream",
    "live stream", "walkthrough",
    # General
    "vlogs", "vlog", "behind the scenes", "blooper",
]

_EDUCATIONAL_KEYWORDS = [
    "tutorial", "lecture", "course", "learn", "how to", "explained",
    "guide", "lesson", "class", "study", "education", "training",
    "workshop", "webinar", "crash course", "full course", "introduction to",
    "beginners guide", "deep dive", "overview",
]


def _keyword_classify(title: str) -> str | None:
    """
    Fast keyword-based pre-filter. Returns a category string or None if
    the title is ambiguous (let the LLM decide).
    """
    lower = title.lower()

    for kw in _ENTERTAINMENT_KEYWORDS:
        if kw in lower:
            print(f"[CLASSIFIER] Keyword match '{kw}' → entertainment")
            return "entertainment"

    # Only trust educational keywords if there are NO entertainment signals
    for kw in _EDUCATIONAL_KEYWORDS:
        if kw in lower:
            print(f"[CLASSIFIER] Keyword match '{kw}' → educational")
            return "educational"

    return None  # ambiguous — fall through to LLM


async def classify_video_content(title: str, transcript_excerpt: str) -> str:
    """
    Returns 'educational', 'entertainment', or 'other'.
    1. Fast keyword check on title.
    2. LLM call for ambiguous titles.
    Fails open to 'educational' only on LLM errors (network/API issues).
    """
    # Step 1 — keyword pre-filter (no API call needed)
    keyword_result = _keyword_classify(title or "")
    if keyword_result is not None:
        return keyword_result

    # Removed hardcoded Groq API check, the LLMFactory will handle provider validation.

    excerpt = (transcript_excerpt or "")[:600].strip()

    prompt = (
        "You are a strict content classifier for an educational course platform.\n\n"
        "Classify the video into EXACTLY ONE category:\n"
        '- "educational": tutorials, lectures, how-to guides, online courses, '
        "explainer videos, documentaries, coding lessons, academic content\n"
        '- "entertainment": music videos, comedy, gaming streams, vlogs, sports '
        "highlights, movies/shows, reaction videos, drama\n"
        '- "other": news, podcasts, interviews, product reviews, advertisements, '
        "political commentary\n\n"
        f"Video Title: {title}\n\n"
        f"Transcript excerpt:\n{excerpt}\n\n"
        "Return ONLY a JSON object with no extra text:\n"
        '{"category": "educational"}'
    )

    try:
        from course_generator.src.core.llm_provider.factory import LLMFactory
        from course_generator.src.core.llm_provider.interfaces import ModelCapability
        
        llm = LLMFactory.get_llm(capability=ModelCapability.FAST_JSON, temperature=0.0)
        
        resp = await llm.ainvoke(prompt)
        raw = resp.content.strip()

        # Strip markdown fences if present
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        parsed = json.loads(raw)
        category = str(parsed.get("category", "educational")).lower()

        if category not in ("educational", "entertainment", "other"):
            print(f"[CLASSIFIER] Unknown category '{category}' — defaulting to educational")
            category = "educational"

        print(f"[CLASSIFIER] '{title}' classified as: {category}")
        return category

    except Exception as exc:
        print(f"[CLASSIFIER] Error (failing open): {exc}")
        return "educational"
