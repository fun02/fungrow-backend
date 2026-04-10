import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ambil API KEY dari Railway
API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/")
def home():
    return "🚀 FUN GROW AI BACKEND ONLINE"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ Error: API_KEY belum diset di Railway."}), 500

        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        
        # Format URL yang paling stabil
        # Perhatikan: Nama model ditulis tanpa prefix 'models/' di dalam variabel agar tidak dobel
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": user_msg}]
            }]
        }

        res = requests.post(url, json=payload, timeout=30)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": f"❌ Google Error: {result['error'].get('message')}"}), 200

        if "candidates" in result:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "⚠️ Google tidak merespon. Cek kuota API Key."}), 200

    except Exception as e:
        return jsonify({"reply": f"❌ Server Error: {str(e)}"}), 500

@app.route("/vision", methods=["POST"])
def vision():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ API_KEY belum diset."}), 500

        file = request.files.get("file")
        img_base64 = base64.b64encode(file.read()).decode("utf-8")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Jelaskan gambar ini."},
                    {"inline_data": {"mime_type": file.mimetype, "data": img_base64}}
                ]
            }]
        }

        res = requests.post(url, json=payload, timeout=30)
        result = res.json()

        if "candidates" in result:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "❌ Gagal analisis gambar."}), 200

    except Exception as e:
        return jsonify({"reply": f"❌ Vision Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
