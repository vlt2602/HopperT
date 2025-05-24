# main.py

import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot, send_summary, send_alert  # 🆕 Gửi tin nhắn tổng hợp và cảnh báo Telegram
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

# ✅ Chạy đồng thời: Telegram Bot + Smart Trade + Vòng lặp trade
async def run_async_tasks():
    await asyncio.gather(
        start_telegram_bot(),
        smart_trade_loop(),
        trade_loop_with_summary()
    )

# 🆕 VÒNG LẶP GIAO DỊCH VỚI XỬ LÝ FALLBACK VÀ THÔNG BÁO GỘP
async def trade_loop_with_summary():
    symbols = ["SHIB/USDT", "DOGE/USDT", "ADA/USDT"]  # 🔥 Danh sách cặp coin (có thể thay đổi)
    current_strategy = "breakout"  # 🔥 Chiến lược hiện tại
    while True:
        skipped_coins = []
        try:
            for symbol in symbols:
                try:
                    winrate = check_winrate(symbol, current_strategy)
                    if winrate < 40:
                        skipped_coins.append(symbol)
                        print(f"⏩ Bỏ qua {symbol} do winrate thấp ({winrate}%).")
                    else:
                        await execute_trade(symbol, current_strategy)
                except Exception as e_symbol:
                    print(f"❌ Lỗi xử lý {symbol}: {e_symbol}")
                    send_alert(f"⚠️ Lỗi xử lý {symbol}: {e_symbol}")
            send_summary(skipped_coins)  # Gửi báo cáo tổng hợp
        except Exception as e_loop:
            print(f"❌ Lỗi vòng lặp trade: {e_loop}")
            send_alert(f"❌ Lỗi vòng lặp trade: {e_loop}")
        await asyncio.sleep(900)  # ⏳ Chờ 15 phút trước vòng lặp tiếp theo

# ✅ KHỞI CHẠY TOÀN HỆ THỐNG
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler_safe).start()
    asyncio.run(run_async_tasks())
