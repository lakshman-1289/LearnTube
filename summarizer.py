from mistralai import Mistral
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mistral client
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def summarize_transcript(transcript, chunk_info=""):
    """
    Summarize a single transcript chunk using Mistral API.
    
    Args:
        transcript: The transcript text to summarize
        chunk_info: Optional info about chunk number (e.g., "Chunk 1 of 3")
    
    Returns:
        Summarized content as string
    """
    print(f"Summarizing transcript {chunk_info}...")
    
    prompt = f"""
    Convert the following video transcript into structured learning notes.

    Include:
    - Title
    - Key Concepts (bullet points)
    - Important Points (detailed)
    - Examples
    - Short Revision Summary

    Make the notes clear, educational, and easy to understand.

    Transcript:
    {transcript}
    """

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert teacher creating clean, well-structured study notes from video transcripts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None


def chunk_text(text, size=2000):
    """
    Split text into chunks by word count.
    
    Args:
        text: The text to chunk
        size: Number of words per chunk
    
    Returns:
        List of text chunks
    """
    print(f"Chunking text into {size}-word chunks...")
    words = text.split()
    chunks = []

    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)

    print(f"Created {len(chunks)} chunks")
    return chunks


def summarize_large_transcript(transcript):
    """
    Summarize large transcripts by splitting into chunks and summarizing each.
    
    Args:
        transcript: The full transcript text
    
    Returns:
        Combined summary of all chunks
    """
    if not transcript or len(transcript.strip()) < 50:
        print("Transcript too short to summarize")
        return "No content available for summarization."
    
    # Check if transcript is large enough to need chunking
    word_count = len(transcript.split())
    
    if word_count < 2000:
        print(f"Transcript is small ({word_count} words), summarizing as single chunk...")
        summary = summarize_transcript(transcript)
        return summary if summary else "Summary could not be generated."
    
    # For large transcripts, use chunking
    print(f"Large transcript detected ({word_count} words), using chunked summarization...")
    chunks = chunk_text(transcript, size=2000)
    
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        summary = summarize_transcript(chunk, chunk_info=f"(Part {i}/{len(chunks)})")
        if summary:
            summaries.append(summary)
    
    if not summaries:
        return "Failed to generate summaries for the transcript."
    
    # Combine all summaries with clear separators
    combined = f"""
=== COMPLETE STUDY NOTES ===

{f"=== Part 1 ===" if len(summaries) > 1 else ""}
{summaries[0]}
"""
    
    for i, summary in enumerate(summaries[1:], 2):
        combined += f"\n\n=== Part {i} ===\n{summary}"
    
    return combined


def generate_quiz_from_notes(notes):
    """
    Generate quiz questions from the study notes.
    
    Args:
        notes: The study notes text
    
    Returns:
        Quiz questions as string
    """
    print("Generating quiz questions from notes...")
    
    prompt = f"""
    Based on the following study notes, create 5 multiple-choice quiz questions.
    
    Format each question as:
    Q1: [Question text]
    a) [Option A]
    b) [Option B]
    c) [Option C]
    d) [Option D]
    Answer: [Correct option letter]
    
    Study Notes:
    {notes}
    """
    
    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educator creating clear, fair quiz questions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None


def save_notes(notes, filename="notes.txt", folder="notes"):
    """
    Save generated notes to a file.
    
    Args:
        notes: The notes content
        filename: Name of the file
        folder: Folder to save in
    
    Returns:
        Path to saved file
    """
    # Create folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    filepath = os.path.join(folder, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(notes)
        print(f"Notes saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving notes: {e}")
        return None
