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
        print(f"❌ Lỗi gửi Telegram: {e}")

def log_error(message):
    print(f"❌ {message}")
    send_telegram(f"❌ {message}")

def log_info(message):
    print(f"ℹ️ {message}")
    send_telegram(f"ℹ️ {message}")
