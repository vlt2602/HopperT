# main.py

import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler

# ✅ Kích hoạt hỗ trợ vòng lặp lồng nhau (bắt buộc trên Replit, Railway)
nest_asyncio.apply()

# ✅ Khởi tạo biến toàn cục điều khiển bot
builtins.bot_active = True

# ✅ Chạy Flask giữ server sống (cổng 8080)
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ✅ Scheduler Telegram báo cáo định kỳ
def run_scheduler_safe():
    try:
        run_scheduler()
    except Exception as e:
        print(f"❌ Lỗi scheduler: {e}")

# ✅ Chạy đồng thời Telegram Bot + Smart Trade Loop
async def run_async_tasks():
    await asyncio.gather(
        start_telegram_bot(),
        smart_trade_loop()
    )

# ✅ Khởi chạy toàn hệ thống trong luồng riêng biệt
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler_safe).start()
    asyncio.run(run_async_tasks())
