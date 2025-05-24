from datetime import datetime, timedelta
import asyncio
import pandas as pd
from binance_handler import binance
from logger import log_info, log_error
from strategy_logger import log_to_sheet, log_strategy
from market_classifier import classify_market_state

# Các thông số mặc định
TIMEFRAME = "5m"
SL_MULTIPLIER = 1.5
TP_MULTIPLIER = 2.0
TRAILING_TRIGGER = 0.5

def calculate_atr(symbol):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=14)
        trs = [abs(c[2] - c[3]) for c in ohlcv[-14:]]
        return sum(trs) / len(trs)
    except Exception as e:
        log_error(f"Lỗi tính ATR: {e}")
        return 0.0

async def monitor_price_and_sell(symbol, qty, entry_price, strategy="auto"):
    atr = calculate_atr(symbol)
    if atr == 0:
        log_info("⚠️ Bỏ qua theo dõi do lỗi tính ATR.")
        return

    sl_price = entry_price - SL_MULTIPLIER * atr
    tp_price = entry_price + TP_MULTIPLIER * atr
    trailing_active = False
    trailing_sl = None

    log_info(f"📉 Theo dõi {symbol} – SL: {sl_price:.2f} | TP: {tp_price:.2f}")
    start_time = datetime.now()

    while (datetime.now() - start_time) < timedelta(minutes=5):
        try:
            price = (await asyncio.to_thread(binance.fetch_ticker, symbol))['last']
            ohlcv_data = await asyncio.to_thread(binance.fetch_ohlcv, symbol, TIMEFRAME, 50)
            df = pd.DataFrame(ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            market_state = classify_market_state(df)

            if not trailing_active and price >= entry_price + (TP_MULTIPLIER * atr * TRAILING_TRIGGER):
                trailing_active = True
                trailing_sl = price - atr * 0.8
                log_info(f"🔁 Trailing Stop kích hoạt tại {price:.2f}")

            exit_trade = (
                (trailing_active and price <= trailing_sl) or
                price >= tp_price or
                price <= sl_price
            )

            if exit_trade:
                result = "win" if price >= tp_price or (trailing_active and price <= trailing_sl) else "loss"
                pnl = (price - entry_price) * qty

                await asyncio.to_thread(binance.create_market_sell_order, symbol, qty)
                log_info(f"{'🟢' if result == 'win' else '🔴'} Đã bán {symbol} tại {price:.2f} | PnL: {pnl:.2f} USDT")

                log_to_sheet(symbol, "SELL", qty, price, strategy, result, round(pnl, 2))
                log_strategy(symbol, strategy, result, pnl, market_state)
                return

            await asyncio.sleep(10)

        except Exception as e:
            log_error(f"❌ Lỗi monitor {symbol}: {e}")
            await asyncio.sleep(5)
