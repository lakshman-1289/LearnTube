from flask import Flask, render_template, request, session, send_file
from transcript import get_transcript
from notes_generator import generate_notes
from quiz_generator import generate_quiz
from topics_generator import generate_topics
from utils import extract_video_id
from summarizer import summarize_large_transcript, generate_quiz_from_notes, save_notes
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

def parse_quiz_text(quiz_text):
    """
    Parse quiz text from AI into structured format for template.
    
    Format expected:
    Q1: Question?
    a) Option A
    b) Option B
    c) Option C
    d) Option D
    Answer: a
    """
    import re
    questions = []
    
    # Split by Q1:, Q2:, etc.
    pattern = r'Q\d+:\s*(.+?)(?=Q\d+:|$)'
    matches = re.findall(pattern, quiz_text, re.DOTALL)
    
    for match in matches:
        lines = match.strip().split('\n')
        if len(lines) >= 5:
            question_text = lines[0].strip()
            options = []
            answer = ""
            
            for line in lines[1:]:
                if line.startswith('a)'):
                    options.append(line[2:].strip())
                elif line.startswith('b)'):
                    options.append(line[2:].strip())
                elif line.startswith('c)'):
                    options.append(line[2:].strip())
                elif line.startswith('d)'):
                    options.append(line[2:].strip())
                elif line.startswith('Answer:'):
                    answer = line.split(':')[1].strip()
            
            if options and answer:
                # Convert answer letter to full text
                answer_index = ord(answer.lower()) - ord('a')
                if 0 <= answer_index < len(options):
                    correct_answer = options[answer_index]
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'answer': correct_answer
                    })
    
    return questions if questions else []

@app.route("/", methods=["GET","POST"])
def index():

    video_id = None
    notes = None
    quiz = None
    topics = []
    error = None
    user_name = None

    if request.method == "POST":

        url = request.form["url"]
        user_name = request.form.get("name", "").strip()

        video_id = extract_video_id(url)

        if video_id:
            try:
                transcript, raw_timestamps = get_transcript(video_id)

                # Use Mistral summarizer for better notes generation
                print("Generating AI-powered study notes using Mistral...")
                notes = summarize_large_transcript(transcript)
                
                # Save notes to file
                notes_filename = f"video_{video_id}_notes.txt"
                save_notes(notes, filename=notes_filename)
    
                # Generate quiz from notes using Mistral
                print("Generating quiz questions from notes...")
                quiz_text = generate_quiz_from_notes(notes)
                
                # Parse quiz text into structured format for template
                if quiz_text:
                    # Use the structured quiz format if available
                    quiz = parse_quiz_text(quiz_text)
                else:
                    # Fallback to simple quiz generation
                    quiz = generate_quiz(transcript)
                
                if not quiz:
                    quiz = []  # Ensure it's an empty list, not None

                # Generate meaningful topics with timestamps
                topics = generate_topics(transcript, raw_timestamps)

                # Store in session for certificate
                session['user_name'] = user_name
                session['video_id'] = video_id
                session['notes'] = notes
                session['quiz'] = quiz
                session['transcript'] = transcript
                session['topics'] = topics

            except Exception as e:
                error = str(e)
                print(f"Error processing video: {error}")
        else:
            error = "Invalid YouTube URL. Please provide a valid YouTube video link."

    return render_template(
        "index.html",
        video_id=video_id,
        notes=notes,
        quiz=quiz,
        topics=topics,
        error=error,
        user_name=user_name,
        transcript=session.get('transcript')
    )

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if 'quiz' not in session:
        return "No quiz available."

    quiz = session['quiz']
    score = 0
    total = len(quiz)

    for i, q in enumerate(quiz):
        user_answer = request.form.get(f'q{i}')
        if user_answer == q['answer']:
            score += 1

    session['score'] = score
    session['total'] = total

    return render_template("result.html", score=score, total=total, percentage=(score/total)*100)

# Add result.html template later

@app.route("/certificate")
def certificate():
    if 'user_name' not in session or 'video_id' not in session:
        return "No course completed yet."

    # Require passing quiz
    if 'score' not in session or session.get('score', 0) / session.get('total', 1) < 0.6:
        return "Complete the quiz with at least 60% to get certificate."

    user_name = session['user_name']
    video_id = session['video_id']

    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Certificate of Completion", styles['Title']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"This certifies that {user_name} has successfully completed the SmartCourse Notes course for video {video_id}.", styles['Normal']))
    story.append(Paragraph(f"Quiz Score: {session['score']}/{session['total']} ({(session['score']/session['total'])*100:.1f}%)", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Date: " + str(__import__('datetime').datetime.now().date()), styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='certificate.pdf', mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)