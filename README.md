# 🎓 SmartCourse Notes - AI-Powered Learning Assistant

> Transform any YouTube video into structured, AI-powered study notes in seconds

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)]()
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)]()
[![Mistral AI](https://img.shields.io/badge/Mistral-AI-blue.svg)]()

---

## 🌟 Features

| Feature | Status | Details |
|---------|--------|---------|
| **YouTube Transcript Extraction** | ✅ Working | Extracts closed captions with timestamps |
| **AI-Powered Note Generation** | ✅ NEW | Mistral Large creates structured notes |
| **Automatic Chunking** | ✅ NEW | Handles long transcripts (1000+ minutes) |
| **Smart Quiz Generation** | ✅ Working | Creates multiple-choice questions |
| **Topic Extraction** | ✅ Working | Generates key topics with timestamps |
| **PDF Certificates** | ✅ Working | Create completion certificates |
| **Notes Saving** | ✅ NEW | Auto-saves to `notes/` folder |
| **Web Interface** | ✅ Working | Beautiful, responsive UI |

---

## 📁 Project Structure

```
smartcourse_notes/
│
├── 📄 Documentation
│   ├── README.md                 ← You are here
│   ├── ADVANCED_FEATURES.md     ← Pro features guide
│   └── FINAL_CHECKLIST.md       ← Setup checklist
│
├── 🐍 Python Modules
│   ├── app.py                   ← Main Flask app
│   ├── summarizer.py            ← Mistral AI integration
│   ├── transcript.py            ← YouTube transcript retrieval
│   ├── quiz_generator.py        ← Quiz generation
│   ├── notes_generator.py       ← Fallback notes generator
│   ├── topics_generator.py      ← Topic extraction
│   └── utils.py                 ← Utility functions
│
├── 🌐 Web Interface
│   ├── templates/
│   │   ├── index.html           ← Main UI
│   │   └── result.html          ← Results page
│   └── static/
│       └── style.css            ← Styling
│
├── 📚 Generated Content
│   └── notes/                   ← Your generated notes
│       └── video_*.txt
│
├── ⚙️ Configuration
│   ├── requirements.txt          ← Dependencies
│   ├── .env                     ← API keys (NEVER commit!)
│   ├── .gitignore               ← Git ignore rules
│   └── .venv/                   ← Virtual environment
│
    └── test_open
```

---

## 🚀 Quick Start (2 minutes)

### 1. Get Mistral API Key

1. Visit: https://console.mistral.ai/api-keys/
2. Create a new API key
3. Copy it

### 2. Configure .env

```bash
# Edit .env file
MISTRAL_API_KEY=your_mistral_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

Then open: **http://127.0.0.1:5000**

---

## 📖 How It Works

```
User enters YouTube URL
        ↓
   Extract Video ID
        ↓
  Get Transcript API
        ↓
 Split into Chunks
  (if needed)
        ↓
 Mistral Large
  Summarization
        ↓
Structured Notes:
• Title
• Key Concepts
• Important Points
• Examples
• Revision Summary
        ↓
 AI Quiz Generation
        ↓
 Topic Extraction
        ↓
Display in Web UI
        ↓
 Save to Disk
```

---

## 💡 Example Workflow

### Input
Copy paste YouTube URL:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Processing
```
✅ Transcript retrieved (12,450 characters)
✅ Split into 6 chunks
⏳ Summarizing chunk 1 of 6...
⏳ Summarizing chunk 2 of 6...
...
✅ All chunks summarized
⏳ Creating master summary...
✅ Notes generated (2,847 characters)
✅ Generating quiz questions...
✅ Extracting topics...
✅ Saving to notes/video_dQw4w9WgXcQ_notes.txt
```

### Output

**Generated Study Notes:**

```
Title: Introduction to Machine Learning

Key Concepts
• Supervised vs Unsupervised Learning
• Training Data and Features
• Model Evaluation Metrics
• Overfitting and Regularization

Important Points
• Proper data splitting prevents model bias
• Cross-validation ensures reliability
• Feature scaling improves model convergence
• Regularization prevents overfitting

Examples
• Email classification (supervised)
• Customer segmentation (unsupervised)
• Time-series prediction (regression)

Quick Revision
Machine learning uses algorithms to find patterns in data.
Success depends on good data, proper features, and careful evaluation.
```

**Auto-Generated Quiz:**

```
Q1: What is the main difference between supervised and unsupervised learning?
a) Supervised uses labeled data, unsupervised doesn't
b) Unsupervised is faster
c) Supervised works with more data
d) They are the same

Answer: a) Supervised uses labeled data, unsupervised doesn't
```

---

## 🔧 Configuration Options

### Change Model

Edit `summarizer.py`, line 23:

```python
model="gpt-4o-mini"  # Change to "gpt-4" or "gpt-3.5-turbo"
```

### Adjust Chunk Size

Edit `summarizer.py`, `chunk_text()` function:

```python
def chunk_text(text, size=2000):  # Change size here
    # ...
```

### Control API Costs

Set max_tokens in `summarizer.py`:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    max_tokens=1500  # Lower = cheaper, but shorter output
)
```

---

## 💰 API Costs

| Item | Cost |
|------|------|
| 1,000 input tokens | $0.00015 |
| 1,000 output tokens | $0.0006 |
| Avg 5-min video | $0.01 |
| Avg 60-min lecture | $0.05-0.10 |

**Tip**: Set spending limits in Mistral dashboard!

---

## 📊 Advanced Features

### Ready to Implement:

1. **Hierarchical Summarization** - For 1+ hour lectures
2. **Auto-Flashcards** - Interactive study cards
3. **Timestamp Notes** - Link notes to video timestamps

See `ADVANCED_FEATURES.md` for full implementation guides.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'mistralai'"

```bash
pip install mistralai python-dotenv
```

### "MISTRAL_API_KEY not found"

Make sure `.env` file has:
```
MISTRAL_API_KEY=your_mistral_key
```

### "Invalid API key"

Check your Mistral API key from console.mistral.ai

### Slow Summarization

Normal! Takes 5-15 seconds per transcript.

### `.env` accidentally committed?

```bash
# Rotate your API key immediately in Mistral dashboard
# Then update .env with new key
```

---

## 📈 Performance Tips

| Optimization | Impact | Difficulty |
|-------------|--------|-----------|
| Use smaller model (gpt-3.5-turbo) | 10x cheaper | Easy |
| Lower max_tokens | Faster + cheaper | Easy |
| Cache summaries | 5x faster on repeat | Medium |
| Parallel API calls | 3x speed | Hard |

---

## 🔐 Security Best Practices

✅ **DO:**
- Store API key in `.env` (never in code)
- Add `.env` to `.gitignore`
- Rotate API keys regularly
- Set spending limits in Mistral

❌ **DON'T:**
- Commit `.env` to Git
- Share your API key
- Put API key in frontend code
- Use production keys in development

---

## 📚 Requirements

- Python 3.10+
- Mistral API key (free account available)
- Internet connection (for API calls)
- ~500MB disk space for notes
- 2GB RAM minimum

---

## 🎯 Use Cases

1. **Students** - Generate study notes from lecture videos
2. **Teachers** - Create quizzes from tutorial content
3. **Content Creators** - Repurpose videos into written guides
4. **Researchers** - Summarize technical talks and presentations
5. **Professionals** - Learn from online courses quickly

---

## 🚀 Roadmap

- [ ] User authentication system
- [ ] Progress tracking dashboard
- [ ] Flashcard export (Anki format)
- [ ] Mobile app
- [ ] Collaborative note sharing
- [ ] Multi-language support
- [ ] Advanced analytics

---

## 🤝 Contributing

Got ideas? Found bugs?

1. Test locally
2. Document changes
3. Submit feedback

---

## 📖 Full Documentation

- **Setup**: Check `FINAL_CHECKLIST.md` first
- **Advanced Features**: See `ADVANCED_FEATURES.md`

---

## 📞 Support

**Common Issues**:
- API not working? → Check `.env` file
- Slow? → Loading is normal (5-15 sec)
- Wrong output? → Try different YouTube video

---

## 📜 License

This project is open source and free to use for educational purposes.

---

## 🎉 You're All Set!

Your AI-powered learning assistant is ready to:
- ✅ Extract transcripts
- ✅ Generate study notes
- ✅ Create quizzes
- ✅ Save for offline review

**Start learning faster today!** 🚀

---

## 🙏 Acknowledgments

- Mistral AI for Large model
- YouTube API for transcript access
- Flask for web framework
- Students everywhere who deserve better learning tools

---

**Made with ❤️ for learners**

*Last Updated: March 8, 2026*
