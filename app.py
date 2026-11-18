import asyncio
import os
from flask import Flask, request, send_file
from flask_cors import CORS
import edge_tts

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'hi-IN-MadhurNeural')

    if not text:
        return {"error": "Text missing"}, 400

    output_file = "output.mp3"

    async def generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

    asyncio.run(generate())
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
