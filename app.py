"""Dialer UI + Telegram bot (Flask).

- Serves the dialer web UI at /
- POST /api/submit  -> sends the entered number to Telegram chat(s)
- POST /webhook/<secret> -> Telegram updates (/start opens the dialer as a Mini App)
Bot token stays on the server (env vars) and never reaches the browser.
"""
import os, re, html, requests
from flask import Flask, request, jsonify, send_from_directory

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")          # where numbers are delivered (your user/group id)
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")  # public https URL of this app
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__, static_folder="static")


def tg(method, **payload):
    return requests.post(f"{API}/{method}", json=payload, timeout=15).json()


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/health")
def health():
    return "ok"


@app.post("/api/submit")
def submit():
    data = request.get_json(silent=True) or {}
    number = str(data.get("number", "")).strip()
    if not re.fullmatch(r"\+?[\d*#]{7,18}", number):
        return jsonify(ok=False, error="Invalid number"), 400
    if not BOT_TOKEN or not CHAT_ID:
        return jsonify(ok=False, error="Server not configured"), 500
    u = data.get("user") or {}
    who = html.escape(" ".join(filter(None, [u.get("first_name"), u.get("last_name")])) or "Web visitor")
    uname = f" (@{html.escape(u['username'])})" if u.get("username") else ""
    text = f"📞 <b>New number</b>\n<code>{html.escape(number)}</code>\n👤 {who}{uname}"
    r = tg("sendMessage", chat_id=CHAT_ID, text=text, parse_mode="HTML")
    if not r.get("ok"):
        return jsonify(ok=False, error="Telegram error"), 502
    return jsonify(ok=True)


@app.post("/webhook/<secret>")
def webhook(secret):
    if secret != WEBHOOK_SECRET:
        return "forbidden", 403
    msg = (request.get_json(silent=True) or {}).get("message") or {}
    chat_id = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").strip()
    if chat_id and text.startswith("/start"):
        tg("sendMessage", chat_id=chat_id, text="📞 Dialer खोलने के लिए नीचे बटन दबाएँ",
           reply_markup={"inline_keyboard": [[{"text": "📞 Open Dialer", "web_app": {"url": BASE_URL}}]]})
    return "ok"


@app.get("/setup")
def setup():
    """Visit once after deploy: registers webhook + menu button."""
    if request.args.get("key") != WEBHOOK_SECRET:
        return "forbidden", 403
    a = tg("setWebhook", url=f"{BASE_URL}/webhook/{WEBHOOK_SECRET}")
    b = tg("setChatMenuButton", menu_button={"type": "web_app", "text": "Dialer", "web_app": {"url": BASE_URL}})
    return jsonify(webhook=a, menu=b)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
