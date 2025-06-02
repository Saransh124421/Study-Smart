# 🎥 AI Video Assistant Backend

This is a Flask-based backend application that:

- Downloads audio from YouTube videos
- Transcribes the audio using OpenAI’s `whisper`
- Generates summaries or answers questions using Google’s Gemini API

---

## 🚀 Features

- 🎧 Extracts high-quality audio from YouTube videos
- 🧠 Uses Whisper to transcribe speech to text
- 💡 Sends transcript to Gemini (Gemini 2 Flash) to summarize or answer questions
- 🔥 REST API with CORS support for easy frontend integration

---

## 🛠️ Requirements

### Python Packages

Install dependencies using:

```bash
pip install -r requirements.txt

Flask
flask_cors
yt-dlp
openai-whisper
requests

GEMINI_API_KEY=your_gemini_api_key_here

from dotenv import load_dotenv
load_dotenv()
