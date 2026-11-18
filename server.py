
import os
import base64
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")
SARVAM_URL = "https://api.sarvam.ai/text-to-speech"

def detect_language(text):
    if re.search(r'[\u0980-\u09FF]', text):
        return "bn-IN"
    if re.search(r'[\u0900-\u097F]', text):
        return "hi-IN"
    return "en-IN"

@app.route("/")
def home():
    return jsonify({"status": "My TTS Platform backend is running"})

@app.route("/generate", methods=["POST"])
def generate():
    if not SARVAM_API_KEY:
        return jsonify({"error": "Server API key is not configured"}), 500

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    voice = data.get("voice", "Aman")

    if not text:
        return jsonify({"error": "Please enter some text"}), 400

    if len(text) > 10000:
        return jsonify({"error": "Maximum 10000 characters allowed"}), 400

    speaker = {
        "Aman": "shubh_enhi_ads",
        "hf_beta": "simran_en_customer"
    }.get(voice)

    if not speaker:
        return jsonify({"error": "Invalid voice selected"}), 400

    language = detect_language(text)
    audio_parts = []

    try:
        for start in range(0, len(text), 2500):
            chunk = text[start:start + 2500]

            payload = {
                "text": chunk,
                "model": "bulbul:v4-flash",
                "language_code": language,
                "speaker": speaker,
                "output_audio_codec": "mp3"
            }

            response = requests.post(
                SARVAM_URL,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=180
            )

            if response.status_code != 200:
                return jsonify({
                    "error": "Sarvam API error",
                    "details": response.text[:1000]
                }), response.status_code

            result = response.json()
            audio_parts.append(
                base64.b64decode(result["audios"][0])
            )

        combined_audio = BytesIO(b"".join(audio_parts))
        combined_audio.seek(0)

        return send_file(
            combined_audio,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="my-tts-audio.mp3"
        )

    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
  
