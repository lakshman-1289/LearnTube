import re
import json
import os
import tempfile
import subprocess
import requests
import time
from typing import Optional, Dict, Any

from models.schemas import TranscriptSegment
from utils.youtube_utils import extract_video_id, clean_text


# ---------------- GLOBAL SESSION ----------------
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
})


def safe_request(url):
    for i in range(3):
        try:
            return session.get(url, timeout=10)
        except Exception as e:
            print(f"[Retry {i}] {e}")
            time.sleep(2)
    return None


# ---------------- GROQ TRANSLATION (sync) ----------------
def _translate_with_groq(text: str, source_lang: str) -> str:
    """
    Translate a transcript to English using Groq API (synchronous requests).
    Split into 3000-char chunks to stay within token limits.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or not text:
        return text

    CHUNK_SIZE = 3000
    MAX_CHUNKS = 15   # cap to avoid excessive API usage
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)][:MAX_CHUNKS]
    translated = []

    for idx, chunk in enumerate(chunks):
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a professional translator. "
                                "Translate the text to English exactly as provided. "
                                "Output ONLY the translated text — no explanations, no markdown."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Translate the following {source_lang} text to English:\n\n{chunk}"
                            ),
                        },
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                translated.append(
                    resp.json()["choices"][0]["message"]["content"].strip()
                )
            else:
                print(f"[WARN] Translation chunk {idx+1} returned {resp.status_code}, keeping original")
                translated.append(chunk)
        except Exception as e:
            print(f"[WARN] Translation chunk {idx+1} failed: {e}")
            translated.append(chunk)

        if idx < len(chunks) - 1:
            time.sleep(2)   # simple rate-limit guard between chunks

    return " ".join(translated)


# ---------------- STRATEGY 1 — youtube-transcript-api ----------------
def _get_transcript_youtube_api(video_id: str, lang="en"):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
        )

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except (TranscriptsDisabled, NoTranscriptFound):
            return None

        transcript = None

        # 1a. Try manual English
        try:
            transcript = transcript_list.find_manually_created_transcript([lang])
        except Exception:
            pass

        # 1b. Try auto-generated English
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
            except Exception:
                pass

        # 1c. No English at all — fetch raw transcript in whatever language is
        #     available. extract_transcript() will call Groq to translate it.
        #     We do NOT call .translate("en") here because YouTube's translation
        #     endpoint is aggressively rate-limited (429) for server-side requests.
        if transcript is None:
            all_transcripts = (
                list(transcript_list._generated_transcripts.values())
                + list(transcript_list._manually_created_transcripts.values())
            )
            for t in all_transcripts:
                try:
                    transcript = t
                    print(f"[INFO] Found caption in {t.language_code} — will translate via Groq")
                    break
                except Exception:
                    continue

        if transcript is None:
            return None

        data = transcript.fetch()
        segments = [
            {"start": seg["start"], "text": seg.get("text", "").strip()}
            for seg in data
            if seg.get("text")
        ]

        if not segments:
            return None

        return {
            "source": "youtube_transcript_api",
            "language": transcript.language_code,
            "is_generated": getattr(transcript, "is_generated", True),
            "segments": segments,
            "transcript": clean_text(" ".join(s["text"] for s in segments)),
        }

    except Exception as e:
        print("[ERROR] youtube-transcript-api:", e)
        return None


# ---------------- STRATEGY 2 — timedtext ----------------
def _get_transcript_timedtext(video_id: str, lang="en"):
    import xml.etree.ElementTree as ET

    def _fetch_timedtext(vid, language):
        """Fetch and parse a timedtext XML for a given language code."""
        url = f"https://video.google.com/timedtext?v={vid}&lang={language}"
        resp = safe_request(url)
        if not resp or not resp.text.strip():
            return None
        try:
            root = ET.fromstring(resp.text)
        except Exception:
            return None
        segments = []
        for child in root:
            text = child.text.strip() if child.text else ""
            if text:
                segments.append({
                    "start": float(child.attrib.get("start", 0)),
                    "text": text,
                })
        if not segments:
            return None
        return segments

    try:
        # 1. Try requested language (usually "en")
        segments = _fetch_timedtext(video_id, lang)
        if segments:
            return {
                "source": "timedtext",
                "language": lang,
                "is_generated": True,
                "segments": segments,
                "transcript": clean_text(" ".join(s["text"] for s in segments)),
            }

        # 2. Discover available languages via the list endpoint
        list_resp = safe_request(
            f"https://video.google.com/timedtext?type=list&v={video_id}"
        )
        if not list_resp or not list_resp.text.strip():
            return None

        try:
            root = ET.fromstring(list_resp.text)
        except Exception:
            return None

        available_langs = [
            t.attrib.get("lang_code")
            for t in root.iter("track")
            if t.attrib.get("lang_code")
        ]

        for alt_lang in available_langs:
            segments = _fetch_timedtext(video_id, alt_lang)
            if segments:
                print(f"[INFO] timedtext: found captions in {alt_lang} — will translate via Groq")
                return {
                    "source": "timedtext",
                    "language": alt_lang,
                    "is_generated": True,
                    "segments": segments,
                    "transcript": clean_text(" ".join(s["text"] for s in segments)),
                }

        return None

    except Exception as e:
        print("[ERROR] timedtext:", e)
        return None


# ---------------- STRATEGY 3 — yt-dlp ----------------
def _get_transcript_ytdlp(video_id: str, lang="en"):
    import yt_dlp

    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang],
        "skip_download": True,
        "quiet": True,
        "socket_timeout": 15,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
    }

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return None

        all_subs = info.get("subtitles") or {}
        auto_subs = info.get("automatic_captions") or {}

        # Prefer manual subtitles over auto-generated
        merged_subs = {}
        merged_subs.update(auto_subs)
        merged_subs.update(all_subs)

        if not merged_subs:
            return None

        # 1. Prefer exact language match
        sub_url = None
        detected_lang = lang
        for key in merged_subs:
            if key == lang or key.startswith(lang + "-"):
                formats = merged_subs[key]
                if formats:
                    sub_url = formats[0]["url"]
                    detected_lang = key
                    break

        # 2. Fallback: take whatever language is available
        if not sub_url:
            for key, formats in merged_subs.items():
                if formats:
                    detected_lang = key
                    sub_url = formats[0]["url"]
                    print(f"[INFO] yt-dlp: no English subtitles, using {detected_lang}")
                    break

        if not sub_url:
            return None

        resp = safe_request(sub_url)
        if not resp:
            return None

        # Parse JSON3 format
        try:
            data = resp.json()
            segments = []
            for event in data.get("events", []):
                if "segs" not in event:
                    continue
                text = "".join(seg.get("utf8", "") for seg in event["segs"]).strip()
                if text:
                    segments.append({
                        "start": event.get("tStartMs", 0) / 1000,
                        "text": text,
                    })

            if segments:
                return {
                    "source": "yt-dlp",
                    "language": detected_lang,
                    "is_generated": True,
                    "segments": segments,
                    "transcript": clean_text(" ".join(s["text"] for s in segments)),
                }
        except Exception:
            print("[WARN] yt-dlp parsing json failed, trying text fallback")

        # Parse VTT/SRT text fallback
        lines = resp.text.split("\n")
        temp_text = ""
        for line in lines:
            line = line.strip()
            if (
                not line
                or "-->" in line
                or line.startswith("WEBVTT")
                or line.isdigit()
                or line.startswith("Kind:")
                or line.startswith("Language:")
            ):
                continue
            clean_line = re.sub(r"<[^>]+>", "", line)
            if clean_line:
                temp_text += " " + clean_line

        text_content = clean_text(temp_text) if temp_text else clean_text(resp.text)
        if not text_content:
            return None

        return {
            "source": "yt-dlp",
            "language": detected_lang,
            "is_generated": True,
            "segments": [{"start": 0, "text": text_content, "duration": 0}],
            "transcript": text_content,
        }

    except Exception as e:
        print("[ERROR] yt-dlp:", e)
        return None


def _get_video_title_ytdlp(video_id: str) -> str:
    """Get video title using yt-dlp (no download)."""
    try:
        import sys
        cmd = [
            sys.executable, "-m", "yt_dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--get-title",
            "--no-warnings",
            "-q",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


# ---------------- STRATEGY 4 — ASR (Whisper) ----------------
def _get_transcript_asr(video_id: str, lang="en") -> Optional[Dict[str, Any]]:
    import sys
    import shutil

    if not shutil.which("ffmpeg"):
        print("[WARN] ffmpeg not found, skipping ASR fallback")
        return None

    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            raw_audio = os.path.join(temp_dir, "raw_audio.%(ext)s")
            raw_audio_mp3 = raw_audio.replace("%(ext)s", "mp3")
            trimmed_audio = os.path.join(temp_dir, "trimmed_audio.mp3")

            dl_cmd = [
                sys.executable, "-m", "yt_dlp",
                "-x", "--audio-format", "mp3",
                "-o", raw_audio, url,
            ]
            subprocess.run(
                dl_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=120,
            )

            trim_cmd = [
                "ffmpeg", "-y",
                "-i", raw_audio_mp3,
                "-t", "600",
                "-c", "copy",
                trimmed_audio,
            ]
            subprocess.run(
                trim_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=60,
            )

            from faster_whisper import WhisperModel
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments_gen, info_obj = model.transcribe(trimmed_audio)

            segments = []
            for seg in segments_gen:
                if seg.text and seg.text.strip():
                    segments.append({"start": seg.start, "text": seg.text.strip()})

            if not segments:
                return None

            detected_lang = getattr(info_obj, "language", lang)

            return {
                "source": "asr_fallback",
                "language": detected_lang,
                "is_generated": True,
                "segments": segments,
                "transcript": clean_text(" ".join(s["text"] for s in segments)),
            }

    except Exception as e:
        print(f"[ERROR] asr_fallback: {e}")
        return None


# ---------------- MAIN FUNCTION ----------------
def extract_transcript(youtube_url: str, lang="en"):

    video_id = extract_video_id(youtube_url)
    title = _get_video_title_ytdlp(video_id)

    for func in [
        _get_transcript_youtube_api,
        _get_transcript_timedtext,
        _get_transcript_ytdlp,
        _get_transcript_asr,
    ]:
        result = func(video_id, lang)
        if not result or not result.get("segments"):
            continue

        detected_lang = result.get("language", lang)
        print(f"[INFO] Using transcript source: {result['source']}")
        print(f"[INFO] Detected language: {detected_lang}")

        # If the transcript is not in English, translate via Groq
        if not detected_lang.startswith("en") and result.get("transcript"):
            print(f"[INFO] Non-English transcript ({detected_lang}) — translating to English via Groq...")
            translated = _translate_with_groq(result["transcript"], detected_lang)
            result["transcript"] = translated
            # Update segments text so downstream chunking uses the translated text
            result["segments"] = [{"start": 0, "text": translated}]
            result["language"] = f"en-translated-from-{detected_lang}"
            print(f"[INFO] Translation complete ({len(translated)} chars)")

        return _format_output(video_id, result, title)

    print("[WARN] All methods failed to extract transcript.")
    return {
        "videoId": video_id,
        "title": title,
        "metadata": {"source": "none", "language": lang, "is_generated": False},
        "segments": [],
        "transcript": "",
    }


def _format_output(video_id, result, title):
    return {
        "videoId": video_id,
        "title": title,
        "metadata": {
            "source": result["source"],
            "language": result.get("language", "en"),
            "is_generated": result.get("is_generated", True),
        },
        "segments": [
            TranscriptSegment(start=s["start"], text=s["text"])
            for s in result["segments"]
        ],
        "transcript": result["transcript"],
    }
