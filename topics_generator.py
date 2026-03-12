def generate_topics(transcript, raw_timestamps):
    """
    Generate simple topic markers with timestamps
    """
    print("Using simple fallback topics generation")  # Debug

    if not raw_timestamps:
        return []

    topics = []
    # Take first few timestamps as topics
    for i, (timestamp, text) in enumerate(raw_timestamps[:5]):
        if text.strip():
            topic_text = text[:50] + "..." if len(text) > 50 else text
            topics.append({
                'topic': f"Topic {i+1}: {topic_text}",
                'timestamp': int(timestamp)
            })

    print(f"Generated {len(topics)} topics")
    return topics