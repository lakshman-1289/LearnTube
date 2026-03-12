def generate_notes(transcript):
    """
    Fallback notes generation.
    In production, use Mistral integration via summarizer.py
    """
    if not transcript or len(transcript.strip()) < 10:
        return "No transcript available to generate notes."

    # Simple summarization by taking first few sentences
    sentences = transcript.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 3:
        return f"Key points from the video:\n\n• {transcript[:200]}..."

    # Take first 5 sentences as key points
    notes = "Key points from the video:\n\n"
    for sentence in sentences[:5]:
        if sentence:
            notes += f"• {sentence.strip()}.\n\n"

    return notes