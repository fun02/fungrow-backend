import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Memberikan izin akses penuh agar frontend bisa memanggil backend
CORS(app)

# Mengambil API Key dari tab 'Variables' di Railway
API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/")
def home():
    return "🚀 FUN GROW AI BACKEND AKTIF & STABIL"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Cek apakah API Key sudah terpasang di Railway
        if not API_KEY:
            return jsonify({"reply": "❌ Error: API_KEY belum diset di Variables Railway."}), 500

        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        
        if not user_msg:
            return jsonify({"reply": "Pesan kosong."}), 200

        # Gunakan model Gemini 1.5 Flash (Tercepat & Stabil)
        url = f"https://generativelanguage.googleapis.com/v1beta/{get_model()}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": user_msg}]
            }]
        }

        res = requests.post(url, json=payload, timeout=30)
        result = res.json()

        # --- PROTEKSI ERROR 'CANDIDATES' ---
        if "error" in result:
            error_msg = result["error"].get("message", "Unknown API Error")
            return jsonify({"reply": f"❌ Google AI Error: {error_msg}"}), 200

        if "candidates" in result and len(result["candidates"]) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "⚠️ AI tidak memberikan jawaban. Cek kuota API kamu."}), 200

    except Exception as e:
        return jsonify({"reply": f"❌ Server Crash: {str(e)}"}), 500

@app.route("/vision", methods=["POST"])
def vision():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ API_KEY belum diset."}), 500

        file = request.files.get("file")
        if not file:
            return jsonify({"reply": "❌ File gambar tidak ditemukan."}), 400

        # Encode gambar ke Base64
        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Tolong jelaskan isi gambar ini untuk keperluan pendidikan."},
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
            return jsonify({"reply": "❌ Gagal menganalisis gambar. Cek API Key."}), 200

    except Exception as e:
        return jsonify({"reply": f"❌ Vision Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Railway menggunakan port dinamis
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
