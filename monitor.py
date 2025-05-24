import threading
import time
import builtins
from logger import log_error, log_info

def monitor_bot():
    while True:
        try:
            now = time.time()
            if hasattr(builtins, 'last_action_time'):
                last_time = builtins.last_action_time
                if now - last_time > 6 * 3600:  # 6 giờ không hoạt động
                    log_error("⚠️ Bot không hoạt động hơn 6 giờ! Kiểm tra ngay.")
            time.sleep(3600)  # Kiểm tra mỗi giờ
        except Exception as e:
            log_error(f"❌ Lỗi monitor: {e}")
