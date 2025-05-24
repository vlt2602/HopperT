<<<<<<< HEAD
import threading
import asyncio
import builtins
import nest_asyncio
from flask_app import app
from telegram_handler import start_telegram_bot, send_alert  # Xoá send_summary
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler
from strategy_manager import check_winrate, get_best_strategy
from trade_manager import execute_trade

nest_asyncio.apply()
builtins.bot_active = True

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_scheduler_safe():
    try:
        run_scheduler()
    except Exception as e:
        print(f"❌ Lỗi scheduler: {e}")

async def run_async_tasks():
    await asyncio.gather(
        start_telegram_bot(),
        smart_trade_loop(),
        trade_loop_with_summary()
    )

async def trade_loop_with_summary():
    symbols = ["SHIB/USDT", "DOGE/USDT", "ADA/USDT"]
    while True:
        try:
            current_strategy = get_best_strategy()
            print(f"🔥 Sử dụng chiến lược tốt nhất: {current_strategy}")
            for symbol in symbols:
                try:
                    winrate = check_winrate(symbol, current_strategy)
                    if winrate < 40:
                        print(f"⏩ Bỏ qua {symbol} do winrate thấp ({winrate}%).")
                    else:
                        await execute_trade(symbol, current_strategy)
                except Exception as e_symbol:
                    print(f"❌ Lỗi xử lý {symbol}: {e_symbol}")
                    send_alert(f"⚠️ Lỗi xử lý {symbol}: {e_symbol}")
        except Exception as e_loop:
            print(f"❌ Lỗi vòng lặp trade: {e_loop}")
            send_alert(f"❌ Lỗi vòng lặp trade: {e_loop}")
        await asyncio.sleep(900)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler_safe).start()
    asyncio.run(run_async_tasks())
=======
import nest_asyncio
import asyncio
from telegram_handler import start_telegram_bot

# Kích hoạt hỗ trợ vòng lặp lồng nhau
nest_asyncio.apply()

# Khởi chạy bot Telegram
asyncio.get_event_loop().run_until_complete(start_telegram_bot())
>>>>>>> 5a8f10b (Update telegram_handler.py với menu inline mới)
