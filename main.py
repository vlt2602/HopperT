import asyncio
import builtins
import os
from quart import Quart
from smart_handler import smart_trade_loop
from report_scheduler import run_scheduler
from strategy_manager import check_winrate, get_best_strategy
from trade_manager import execute_trade
from logger_helper import log_error, log_info
from binance_handler import get_best_symbols

app = Quart(__name__)
builtins.bot_active = True

@app.route('/')
async def index():
    return 'HopperT is running!'

@app.route('/status')
async def status():
    return {'bot_active': builtins.bot_active}

async def run_scheduler_safe():
    try:
        await asyncio.to_thread(run_scheduler)
    except Exception as e:
        log_error(f"Lỗi scheduler: {e}")

async def trade_loop_with_summary():
    while builtins.bot_active:
        try:
            symbols = get_best_symbols()  # Thay thế danh sách tĩnh
            current_strategy = get_best_strategy()
            log_info(f"Sử dụng chiến lược tốt nhất: {current_strategy}")
            for symbol in symbols:
                try:
                    winrate = check_winrate(symbol, current_strategy)
                    if winrate < 40:
                        log_info(f"Bỏ qua {symbol} do winrate thấp ({winrate}%).")
                    else:
                        await execute_trade(symbol, current_strategy)
                except Exception as e_symbol:
                    log_error(f"Lỗi xử lý {symbol}: {e_symbol}")
        except Exception as e_loop:
            log_error(f"Lỗi vòng lặp trade: {e_loop}")
        await asyncio.sleep(900)

async def main():
    await asyncio.gather(
        app.run_task(host='0.0.0.0', port=int(os.getenv("PORT", 8080))),
        run_scheduler_safe(),
        smart_trade_loop(),
        trade_loop_with_summary()
    )

if __name__ == "__main__":
    asyncio.run(main())
