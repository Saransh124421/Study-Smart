from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yt_dlp
import whisper
import requests
import json
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
GEMINI_API_KEY = "AIzaSyDmxxq0wqT0ctG_JwRn5h2ziWSl3oDM2Yo"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@app.route('/')
def home():
    return "AI Video Assistant Backend is running!"

def download_audio(youtube_url):
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': temp_path.replace('.mp3', ''),  # yt-dlp adds the extension
            'ffmpeg_location': r'C:\ffmpeg\ffmpeg.exe',  # Explicit path to ffmpeg.exe
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Ensure the output file has .mp3 extension
        if not temp_path.endswith('.mp3'):
            os.rename(temp_path, temp_path + '.mp3')
            temp_path += '.mp3'
        
        return temp_path
    except Exception as e:
        print(f"Error in download_audio: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

def transcribe_audio(audio_file, model_size="base"):
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_file)
        return result["text"]
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        raise

def ask_gemini(question, context):
    try:
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Context from a YouTube video transcript: {context}"},
                        {"text": f"Question: {question}"},
                        {"text": "Please provide a concise answer based on the transcript."}
                    ]
                }
            ]
        }
        
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        return "Sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        print(f"Error in ask_gemini: {str(e)}")
        raise

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        data = request.json
        print("Received data:", data)  # Debug log
        
        youtube_url = data.get('youtube_url')
        action = data.get('action', 'summary')
        question = data.get('question', 'Summarize this video')
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        # Step 1: Download audio
        audio_file = download_audio(youtube_url)
        print("Audio downloaded to:", audio_file)  # Debug log
        
        # Step 2: Transcribe audio
        transcript = transcribe_audio(audio_file)
        print("Transcript generated")  # Debug log
        
        # Step 3: Process based on action
        if action == 'transcript':
            response = transcript
        else:
            if action == 'summary':
                question = "Provide a comprehensive summary of the key points in this video"
            response = ask_gemini(question, transcript)
            print("Gemini response generated")  # Debug log
        
        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        return jsonify({
            'transcript': transcript,
            'response': response,
            'question': question,
            'status': 'success'
        })
        
    except Exception as e:
        print("Error in process_video:", str(e))  # Debug log
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)