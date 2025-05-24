import threading
import time
import builtins
from telegram_handler import send_alert

def monitor_bot():
    while True:
        try:
            now = time.time()
            if hasattr(builtins, 'last_action_time'):
                last_time = builtins.last_action_time
                if now - last_time > 6 * 3600:  # 6 giờ không hoạt động
                    send_alert("⚠️ Bot không hoạt động hơn 6 giờ! Kiểm tra ngay.")
            time.sleep(3600)  # Kiểm tra mỗi giờ
        except Exception as e:
            print(f"❌ Lỗi monitor: {e}")
