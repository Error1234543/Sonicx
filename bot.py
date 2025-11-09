import os
import time
import json
import logging
import telebot
from telebot import types

logging.basicConfig(level=logging.INFO)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "7447651332"))
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "https://raw.githubusercontent.com/Error1234543/Sonicx/main/")
CHANNEL_USERNAME = "@NEET_JEE_GUJ"  # replace with your Telegram channel
# ---------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

# ---------- LOAD LOCAL JSON -----------------
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Cannot load data.json: {e}")
        return {}

# ---------- START / REFRESH ----------------
@bot.message_handler(commands=['start', 'refresh'])
def start_menu(msg):
    data = load_data()
    if not data:
        bot.reply_to(msg, "⚠️ Unable to load data.json.")
        return
    
    # Join channel + Close button
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"),
        types.InlineKeyboardButton(text="❌ Close", callback_data="CLOSE")
    )
    bot.send_message(msg.chat.id,
                     "👋 Welcome! Please join our channel to access tests:",
                     reply_markup=kb)

# ---------- CALLBACK HANDLER ----------------
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    data = load_data()
    try:
        if call.data == "CLOSE":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
        
        parts = call.data.split("|")
        if parts[0] == "STD":
            cat = parts[1]
            items = data.get(cat, {})
            kb = types.InlineKeyboardMarkup()
            if isinstance(items, dict):
                # STD → Subjects
                for sub in items.keys():
                    kb.add(types.InlineKeyboardButton(
                        text=sub,
                        callback_data=f"SUBJECT|{cat}|{sub}"
                    ))
            elif isinstance(items, list):
                # Direct test list (Mock/Gujcet)
                for t in items:
                    kb.add(types.InlineKeyboardButton(
                        text=t["label"],
                        web_app=types.WebAppInfo(WEB_BASE_URL + t["path"])
                    ))
            kb.add(types.InlineKeyboardButton("⬅️ Back", callback_data="BACK_MAIN"))
            bot.edit_message_text(f"📚 {cat} - Select:", call.message.chat.id, call.message.message_id, reply_markup=kb)

        elif parts[0] == "SUBJECT":
            cat, subject = parts[1], parts[2]
            tests = data.get(cat, {}).get(subject, [])
            kb = types.InlineKeyboardMarkup()
            for t in tests:
                kb.add(types.InlineKeyboardButton(
                    text=t["label"],
                    web_app=types.WebAppInfo(WEB_BASE_URL + t["path"])
                ))
            kb.add(types.InlineKeyboardButton("⬅️ Back", callback_data=f"STD|{cat}"))
            bot.edit_message_text(f"🧪 {cat} → {subject} - Select Test:", call.message.chat.id, call.message.message_id, reply_markup=kb)

        elif parts[0] == "BACK_MAIN":
            start_menu(call.message)
        else:
            bot.answer_callback_query(call.id, "⚠️ Unknown action")
            
    except Exception as e:
        logging.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "⚠️ Something went wrong.")

# ---------- HELP --------------------------
@bot.message_handler(commands=['help'])
def help_cmd(m):
    text = (
        "📚 *Study Bot Help*\n\n"
        "• /start - Show main menu\n"
        "• /refresh - Reload JSON\n"
        "• Add new tests by updating data.json in your repo.\n\n"
        "Bot auto-syncs from local JSON 🔄"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

# ---------- POLLING ------------------------
if __name__ == "__main__":
    logging.info("🤖 Bot started")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=50)
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(5)