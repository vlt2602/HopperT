# main.py

import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler

# ✅ Bắt buộc trên Replit
nest_asyncio.apply()
builtins.bot_active = True


# ✅ Chạy Flask server giữ Replit sống
def run_flask():
    app.run(host='0.0.0.0', port=8080)


# ✅ Chạy Scheduler riêng
def run_scheduler_safe():
    try:
        run_scheduler()
    except Exception as e:
        print("❌ Lỗi scheduler:", e)


# ✅ Chạy Telegram + Smart Trade song song
async def run_async_tasks():
    await asyncio.gather(start_telegram_bot(), smart_trade_loop())


# ✅ Chạy tất cả trong các luồng riêng biệt
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler_safe).start()
    asyncio.run(run_async_tasks())
