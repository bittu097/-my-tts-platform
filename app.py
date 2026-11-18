from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os

app = Flask(__name__)
CORS(app)

# Yahan tumhara secret password set hai. Tum chaho toh 'Bittu@1990' ki jagah kuch aur likh sakte ho.
SECRET_PASSCODE = "N@@ni-M@@760"

async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    
    # SECURITY LOCK: Agar password match nahi hua toh audio nahi banegi
    if data.get('passcode') != SECRET_PASSCODE:
        return jsonify({"error": "Access Denied: Galat Password!"}), 401
        
    text = data.get('text')
    voice = data.get('voice', 'hi-IN-MadhurNeural')
    
    if not text:
        return jsonify({"error": "Text missing"}), 400
        
    output_file = "output.mp3"
    asyncio.run(generate_audio(text, voice, output_file))
    
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    
