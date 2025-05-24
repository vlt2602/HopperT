# logger_helper.py

from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram: {e}")

def log_error(message):
    try:
        print(f"❌ {message}")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ {message}")
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram log: {e}")

def log_info(message):
    try:
        print(f"ℹ️ {message}")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"ℹ️ {message}")
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram log: {e}")
