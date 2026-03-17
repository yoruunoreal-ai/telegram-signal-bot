from telethon import TelegramClient, events
import re
import os
from flask import Flask
import threading

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]

source_group = -3026686847
target_group = -3780005944

client = TelegramClient("session", api_id, api_hash)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot attivo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def format_signal(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    sl_match = re.search(r'SL[:\s]*([\d\.]+)', text, re.IGNORECASE)
    tp_matches = re.findall(r'TP\d[:\s]*([\d\.]+)', text, re.IGNORECASE)

    main_line_match = re.search(r'(SELL|BUY)\s+[A-Z]{3,6}\s+[\d\.]+', text, re.IGNORECASE)
    main_line = main_line_match.group(0) if main_line_match else ""

    formatted = main_line + "\n"

    if sl_match:
        formatted += f"SL: {sl_match.group(1)}\n"

    for i, tp in enumerate(tp_matches, start=1):
        formatted += f"TP{i}: {tp}\n"

    return formatted.strip()

@client.on(events.NewMessage(chats=source_group))
async def forward_signal(event):
    text = event.message.text
    if text and ('SELL' in text.upper() or 'BUY' in text.upper()):
        new_text = format_signal(text)
        await client.send_message(target_group, new_text)

print("Bot avviato...")

threading.Thread(target=run_web).start()

client.start()
client.run_until_disconnected()
