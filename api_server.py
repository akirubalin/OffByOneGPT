from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

# Reuse your logic
import wrong_bot  # imports your answer(q) and loads .env inside wrong_bot

app = Flask(__name__, static_folder=".", static_url_path="")

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json() or {}
    q = (data.get("q") or "").strip()
    if not q:
        return jsonify({"a": ""})
    a = wrong_bot.answer(q)   # <— reuse your model + wrongify logic
    return jsonify({"a": a})

if __name__ == "__main__":
    # VS Code will attach and auto-open the URL (see launch.json below)
    app.run(host="127.0.0.1", port=5050, debug=True)
