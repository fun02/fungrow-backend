import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# PENGATURAN API - LANGSUNG DEFINISIKAN DISINI
# ==========================================
# Ini memperbaiki error "API_KEY tidak didefinisikan"
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-1.5-flash" # Gunakan 1.5 Flash (Stabil)

@app.route("/")
def home():
    return "🚀 FUN GROW AI BACKEND AKTIF & STABIL"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Validasi API KEY
        if not API_KEY:
            return jsonify({"reply": "❌ Error: API_KEY belum diset di Variables Railway."}), 500

        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        
        if not user_msg:
            return jsonify({"reply": "Pesan kosong."}), 200

        # Endpoint menggunakan v1beta agar mendukung fitur terbaru
        url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": user_msg}]}]
        }

        res = requests.post(url, json=payload, timeout=30)
        result = res.json()

        # Cek Error dari Google
        if "error" in result:
            return jsonify({"reply": f"❌ Google AI Error: {result['error'].get('message')}"}), 200

        # Ambil Balasan
        if "candidates" in result and len(result["candidates"]) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "⚠️ AI tidak merespon. Cek kuota API Key kamu."}), 200

    except Exception as e:
        # Menangkap error coding agar tidak crash tanpa pesan
        return jsonify({"reply": f"❌ Server Error: {str(e)}"}), 500

@app.route("/vision", methods=["POST"])
def vision():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ API_KEY belum diset."}), 500

        file = request.files.get("file")
        if not file:
            return jsonify({"reply": "❌ Gambar tidak ditemukan."}), 400

        img_base64 = base64.b64encode(file.read()).decode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Tolong jelaskan isi gambar ini."},
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
