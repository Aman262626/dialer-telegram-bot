# 📞 Dialer Bot

Caller-style dialer UI (HTML) connected to a Telegram bot. Enter a number on the keypad, press the green call button, and it is delivered to your Telegram chat. Opens inside Telegram as a Mini App.

## Deploy (Railway / Render / any host)
1. Create a bot with [@BotFather](https://t.me/BotFather) → copy token.
2. Get your chat id (e.g. via @userinfobot).
3. Set env vars (see `.env.example`): `BOT_TOKEN`, `CHAT_ID`, `BASE_URL`, `WEBHOOK_SECRET`.
4. Deploy this repo (Procfile included).
5. Open `BASE_URL/setup?key=WEBHOOK_SECRET` once to register webhook + menu button.
6. Send `/start` to your bot → tap **Open Dialer**.

## Local run
```
pip install -r requirements.txt
cp .env.example .env  # then export the vars
python app.py
```
The bot token is only used server-side; never put it in the HTML.
