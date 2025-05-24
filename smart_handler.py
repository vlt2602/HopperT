import asyncio
import builtins
import pandas as pd
from binance_handler import binance, get_best_symbols
from price_watcher import monitor_price_and_sell
from logger_helper import log_error, log_info
from strategy_logger import log_to_sheet
from ai_strategy import select_timeframe
from market_classifier import classify_market_state
from risk_manager import check_daily_loss
from strategy_metrics import get_strategy_scores, get_optimal_usdt_amount
from strategy_manager import get_best_strategy

async def smart_trade_loop():
    while builtins.bot_active:
        log_info("🤖 Bắt đầu vòng lặp giao dịch thông minh...")
        symbols = get_best_symbols()
        current_strategy = get_best_strategy()

        for symbol in symbols:
            try:
                timeframe = select_timeframe(symbol)
                ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

                # Ẩn các thông báo spam như đang xét dữ liệu...
                balance = binance.fetch_balance()['USDT']['free']
                price = binance.fetch_ticker(symbol)['last']
                amount_usdt = min(get_optimal_usdt_amount(current_strategy), balance)

                if amount_usdt < 10:
                    log_error(f"🚨 Không đủ USDT cho {symbol}. Bot tạm dừng.")
                    builtins.bot_active = False
                    return

                qty = round(amount_usdt / price, 5)
                binance.create_market_buy_order(symbol, qty)
                log_info(f"🚀 Đã mua {symbol} {qty} tại {price}")
                log_to_sheet(symbol, "BUY", qty, price, current_strategy, "pending", 0)
                await asyncio.to_thread(monitor_price_and_sell, symbol, qty, price, current_strategy)
                check_daily_loss()
                await asyncio.sleep(2)
            except Exception as e:
                log_error(f"❌ Lỗi xử lý {symbol}: {e}")
        await asyncio.sleep(60)
