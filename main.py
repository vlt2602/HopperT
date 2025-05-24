# main.py

import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot, send_summary  # 🆕 Thêm import send_summary
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler
from strategy_manager import check_winrate  # 🆕 Thêm kiểm tra winrate
from trade_manager import execute_trade  # 🆕 Hàm xử lý giao dịch giả định (ví dụ)

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

# ✅ Chạy đồng thời Telegram Bot + Smart Trade Loop + kiểm tra winrate
async def run_async_tasks():
    await asyncio.gather(
        start_telegram_bot(),
        smart_trade_loop(),
        trade_loop_with_summary()  # 🆕 Thêm trade loop gộp báo cáo
    )

# 🆕 TẠO VÒNG LẶP GIAO DỊCH VỚI THÔNG BÁO GỘP
async def trade_loop_with_summary():
    symbols = ["SHIB/USDT", "DOGE/USDT", "ADA/USDT"]  # 📝 Thay bằng danh sách cặp coin thực tế
    current_strategy = "breakout"  # 📝 Chiến lược hiện tại, có thể lấy từ config hoặc AI
    while True:
        skipped_coins = []
        for symbol in symbols:
            if check_winrate(symbol, current_strategy) < 40:
                skipped_coins.append(symbol)
                print(f"⏩ Bỏ qua {symbol} do winrate thấp.")
            else:
                await execute_trade(symbol, current_strategy)  # 📝 Thay bằng hàm xử lý giao dịch thực
        send_summary(skipped_coins)
        await asyncio.sleep(900)  # 🕒 Chờ 15 phút trước vòng tiếp theo (hoặc tuỳ chỉnh)

# ✅ Khởi chạy toàn hệ thống trong luồng riêng biệt
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler_safe).start()
    asyncio.run(run_async_tasks())
