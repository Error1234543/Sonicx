import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from telebot import types

# ---------- CONFIG ----------
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "@NEET_JEE_GUJ"  # Telegram channel username
bot = telebot.TeleBot(BOT_TOKEN)

JSON_FILE = "data.json"

# ---------- HEALTH CHECK SERVER ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    server = HTTPServer(("0.0.0.0", 8000), HealthHandler)
    print("🌐 Health-check server running on port 8000")
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ---------- LOAD JSON ----------
def load_data():
    if not os.path.exists(JSON_FILE):
        return {}
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ---------- START / CHANNEL JOIN ----------
@bot.message_handler(commands=["start"])
def start_menu(msg):
    chat_id = msg.chat.id
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="✅ Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}"))
    kb.add(types.InlineKeyboardButton(text="❌ Skip", callback_data="SKIP_CHANNEL"))
    bot.send_message(chat_id, "📢 Please join our Telegram channel to continue:", reply_markup=kb)

# ---------- CALLBACK HANDLER ----------
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    try:
        parts = call.data.split("|")
        chat_id = call.message.chat.id

        if call.data == "SKIP_CHANNEL":
            # Show class menu after channel prompt
            kb = types.InlineKeyboardMarkup()
            for std in data.keys():
                kb.add(types.InlineKeyboardButton(text=std, callback_data=f"STD|{std}"))
            bot.edit_message_text("📘 Select Class:", chat_id, call.message.message_id, reply_markup=kb)

        elif parts[0] == "STD":
            std = parts[1]
            kb = types.InlineKeyboardMarkup()
            for subj in data[std].keys():
                kb.add(types.InlineKeyboardButton(
                    text=subj, callback_data=f"SUBJ|{std}|{subj}"))
            kb.add(types.InlineKeyboardButton("⬅️ Back", callback_data="BACK_MAIN"))
            bot.edit_message_text(f"📘 {std}\nSelect Subject:", chat_id, call.message.message_id, reply_markup=kb)

        elif parts[0] == "SUBJ":
            std, subj = parts[1], parts[2]
            kb = types.InlineKeyboardMarkup()
            for t in data[std][subj]:
                file_path = t["path"]
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    kb.add(types.InlineKeyboardButton(
                        text=t["label"], web_app=types.WebAppInfo("data:text/html," + html_content)))
                else:
                    kb.add(types.InlineKeyboardButton(text=f"{t['label']} ❌ Missing", callback_data="MISSING"))
            kb.add(types.InlineKeyboardButton("⬅️ Back", callback_data=f"STD|{std}"))
            bot.edit_message_text(f"🧪 {std} → {subj}\nSelect Test:", chat_id, call.message.message_id, reply_markup=kb)

        elif parts[0] == "BACK_MAIN":
            kb = types.InlineKeyboardMarkup()
            for std in data.keys():
                kb.add(types.InlineKeyboardButton(text=std, callback_data=f"STD|{std}"))
            bot.edit_message_text("📘 Select Class:", chat_id, call.message.message_id, reply_markup=kb)

        else:
            bot.answer_callback_query(call.id, "Unknown action")

    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Something went wrong.")
        print("Callback error:", e)

# ---------- RUN BOT ----------
print("🤖 Bot started")
bot.infinity_polling()