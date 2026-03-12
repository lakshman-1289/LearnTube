import random

def generate_quiz(transcript):
    """"\n    Fallback quiz generation.\n    In production, use Mistral integration via summarizer.py\n    """
    if not transcript or len(transcript.strip()) < 20:
        return []

    # Split transcript into sentences
    sentences = [s.strip() for s in transcript.split('.') if s.strip()]

    if len(sentences) < 1:
        return []

    questions = []

    # Generate up to 5 questions
    for i in range(min(5, len(sentences))):
        try:
            sentence = sentences[i]
            words = sentence.split()

            # Find important words (simple heuristic)
            important_words = [word for word in words if len(word) > 3 and word.lower() not in ['that', 'this', 'with', 'from', 'they', 'them', 'then', 'than', 'will', 'were', 'have', 'been', 'very', 'much', 'many', 'some', 'such', 'only', 'also', 'even', 'just', 'still', 'what', 'when', 'where', 'how', 'why', 'who', 'which']]

            if len(important_words) >= 1:
                key_word = important_words[0]
                question_text = f"What is discussed regarding '{key_word}'?"
                correct_answer = f"The topic of {key_word.lower()}"

                options = [
                    correct_answer,
                    f"Examples of {key_word.lower()}",
                    f"Details about {key_word.lower()}",
                    f"The importance of {key_word.lower()}"
                ]

                random.shuffle(options)

                question = {
                    "question": question_text,
                    "options": options,
                    "answer": correct_answer
                }
                questions.append(question)

        except Exception:
            continue

    # If no questions generated, create a generic one
    if not questions:
        question = {
            "question": "What is the main topic of this video?",
            "options": [
                "The content discussed in the video",
                "A specific example shown",
                "Technical details",
                "General information"
            ],
            "answer": "The content discussed in the video"
        }
        questions.append(question)

    return questions