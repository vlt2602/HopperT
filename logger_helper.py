# logger_helper.py

import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("⚠️ Telegram API lỗi:", response.text)
    except Exception as e:
        print("❌ Lỗi gửi Telegram:", e)
