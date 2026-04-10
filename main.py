import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mengambil API Key dari tab Variables di Railway
API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/")
def home():
    return "🚀 FunGrow AI Backend is Running!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        if not user_msg: return jsonify({"reply": "Pesan kosong"}), 200

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": user_msg}]}]
        }
        res = requests.post(url, json=payload)
        result = res.json()
        
        reply = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/vision", methods=["POST"])
def vision():
    try:
        file = request.files.get("file")
        img_base64 = base64.b64encode(file.read()).decode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Jelaskan gambar ini."},
                    {"inline_data": {"mime_type": file.mimetype, "data": img_base64}}
                ]
            }]
        }
        res = requests.post(url, json=payload)
        result = res.json()
        reply = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error vision: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
