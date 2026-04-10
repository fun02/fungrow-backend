import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")

# 🔥 Model fallback (kalau satu mati, pindah)
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def call_gemini(payload):
    for model in MODELS:
        try:
            url = f"{BASE_URL}/{model}:generateContent?key={API_KEY}"
            
            res = requests.post(url, json=payload, timeout=20)
            result = res.json()

            print("MODEL:", model)
            print("STATUS:", res.status_code)
            print("RESPONSE:", result)

            if res.status_code == 200 and "candidates" in result:
                return result['candidates'][0]['content']['parts'][0]['text']

        except Exception as e:
            print("ERROR:", str(e))
            continue

    return "❌ AI sedang sibuk / error. Coba lagi nanti."

@app.route("/")
def home():
    return "🚀 FUN GROW AI BACKEND ONLINE"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset di Railway"}), 500

        data = request.get_json(force=True)
        user_msg = data.get("message", "")

        if not user_msg:
            return jsonify({"reply": "❌ Pesan kosong"}), 400

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_msg}]
                }
            ]
        }

        reply = call_gemini(payload)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Server error"}), 500


@app.route("/vision", methods=["POST"])
def vision():
    try:
        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset"}), 500

        file = request.files.get("file")

        if not file:
            return jsonify({"reply": "❌ File tidak ditemukan"}), 400

        img_base64 = base64.b64encode(file.read()).decode("utf-8")

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Jelaskan gambar ini dengan detail."},
                        {
                            "inline_data": {
                                "mime_type": file.mimetype,
                                "data": img_base64
                            }
                        }
                    ]
                }
            ]
        }

        reply = call_gemini(payload)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": "❌ Vision error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
