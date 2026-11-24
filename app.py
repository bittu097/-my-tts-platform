from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import time
import uuid

app = Flask(__name__)
CORS(app)

SECRET_PASSCODE = "N@@ni-M@@760"
AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def cleanup_old_files(max_age_seconds=300):
    now = time.time()
    for fname in os.listdir(AUDIO_DIR):
        fpath = os.path.join(AUDIO_DIR, fname)
        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > max_age_seconds:
            try:
                os.remove(fpath)
            except OSError:
                pass


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(silent=True) or {}

    if data.get('passcode') != SECRET_PASSCODE:
        return jsonify({"error": "Access Denied: Galat Password!"}), 401

    text = (data.get('text') or "").strip()
    voice = data.get('voice') or 'hi-IN-MadhurNeural'

    if not text:
        return jsonify({"error": "Text missing"}), 400

    cleanup_old_files()
    output_file = os.path.join(AUDIO_DIR, f"{uuid.uuid4().hex}.mp3")

    try:
        asyncio.run(generate_audio(text, voice, output_file))
        return send_file(output_file, mimetype="audio/mpeg", as_attachment=True, download_name="afsar_studio_voice.mp3")
    except Exception as exc:
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass
        return jsonify({"error": f"Audio generation failed: {str(exc)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
