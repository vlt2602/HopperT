# main.py

import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot, send_summary  # 🆕 Gửi tin nhắn tổng hợp Telegram
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler
from strategy_manager import check_winrate  # 🆕 Kiểm tra winrate từng cặp coin
from trade_manager import execute_trade  # 🆕 Hàm xử lý giao dịch (thực hiện lệnh)

# ✅ Kích hoạt hỗ trợ vòng lặp lồng nhau (Replit, Railway bắt buộc)
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

# ✅ Chạy đồng thời: Telegram Bot + Smart Trade + Gửi thông báo tổng hợp
async def run_async_tasks():
    await asyncio.gather(
        start_telegram_bot(),        # Bot Telegram
        smart_trade_loop(),          # Vòng lặp giao dịch thông minh (đã có)
        trade_loop_with_summary()    # 🆕 Vòng lặp kiểm tra winrate + gửi tin nhắn gộp
    )

# 🆕 VÒNG LẶP GIAO DỊCH VỚI THÔNG BÁO GỘP TELEGRAM
async def trade_loop_with_summary():
    symbols = ["SHIB/USDT", "DOGE/USDT", "ADA/USDT"]  # 🔥 Danh sách cặp coin (anh có thể thay đổi)
    current_strategy = "breakout"  # 🔥 Chiến lược hiện tại (có thể lấy từ config hoặc AI)
    while True:
        skipped_coins = []
        for symbol in symbols:
            try:
                winrate = check_winrate(symbol, current_strategy)
                if winrate < 40:
                    skipped_coins.append(symbol)
                    print(f"⏩ Bỏ qua {symbol} do winrate thấp ({winrate}%).")
                else:
                    await execute_trade(symbol, current_strategy)  # Thực hiện giao dịch
            except Exception as e:
                print(f"❌ Lỗi xử lý {symbol}: {e}")
        # Gửi tin nhắn tổng hợp về Telegram
        send_summary(skipped_coins)
        await asyncio.sleep(900)  # ⏳ Chờ 15 phút (900 giây) rồi lặp lại (anh có thể chỉnh)

# ✅ KHỞI CHẠY TOÀN HỆ THỐNG
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()            # Flask giữ server sống
    threading.Thread(target=run_scheduler_safe).start()   # Scheduler báo cáo định kỳ
    asyncio.run(run_async_tasks())                        # Chạy 3 tác vụ đồng thời
