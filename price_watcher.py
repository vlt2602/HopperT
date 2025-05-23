# price_watcher.py

from datetime import datetime, timedelta
import time
import pandas as pd
from binance_handler import binance
from logger_helper import send_telegram
from strategy_logger import log_to_sheet, log_strategy
from market_classifier import classify_market_state

# Tham số điều chỉnh theo chiến lược
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
        send_telegram(f"❌ Lỗi tính ATR {symbol}: {e}")
        return 0.0

def monitor_price_and_sell(symbol, qty, entry_price, strategy="auto"):
    atr = calculate_atr(symbol)
    if atr == 0:
        send_telegram(f"⚠️ Bỏ qua theo dõi {symbol} do ATR lỗi.")
        return

    sl_price = entry_price - SL_MULTIPLIER * atr
    tp_price = entry_price + TP_MULTIPLIER * atr
    trailing_active = False
    trailing_sl = None

    send_telegram(f"📉 Theo dõi {symbol} – SL: {sl_price:.2f} | TP: {tp_price:.2f}")
    start_time = datetime.now()

    while (datetime.now() - start_time) < timedelta(minutes=5):
        try:
            price = binance.fetch_ticker(symbol)['last']
            ohlcv = binance.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=50)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            market_state = classify_market_state(df)

            # Kích hoạt trailing stop nếu đạt đủ ngưỡng lợi nhuận
            if not trailing_active and price >= entry_price + (TP_MULTIPLIER * atr * TRAILING_TRIGGER):
                trailing_active = True
                trailing_sl = price - atr * 0.8
                send_telegram(f"🔁 Trailing Stop kích hoạt tại {price:.2f}")

            # Điều kiện chốt lệnh: TP / SL / trailing SL
            if (trailing_active and price <= trailing_sl) or price >= tp_price or price <= sl_price:
                result = "win" if price >= tp_price or (trailing_active and price <= trailing_sl) else "loss"
                pnl = round((price - entry_price) * qty, 2)

                binance.create_market_sell_order(symbol, qty)
                send_telegram(f"{'🟢' if result == 'win' else '🔴'} Đã bán {symbol} tại {price:.2f} | PnL: {pnl:.2f} USDT")
                log_to_sheet(symbol, "SELL", qty, price, strategy, result, pnl)
                log_strategy(symbol, strategy, result, pnl, market_state)
                return

            time.sleep(10)

        except Exception as e:
            send_telegram(f"❌ Lỗi theo dõi giá {symbol}: {e}")
            time.sleep(5)
