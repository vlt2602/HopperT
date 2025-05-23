# binance_handler.py

import ccxt
import time
from datetime import datetime, timedelta
import pandas as pd
from logger_helper import send_telegram
from strategy_logger import log_to_sheet, log_strategy

# ✅ CHỈ import classify_market_state (không import monitor từ ai_strategy nữa)
from ai_strategy import classify_market_state

# Khởi tạo đối tượng Binance
binance = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 10000
})

# Danh sách các cặp USDT phổ biến
STABLE_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "DOT/USDT", "AVAX/USDT",
    "SHIB/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "TRX/USDT",
    "LINK/USDT", "ATOM/USDT", "APT/USDT", "NEAR/USDT", "FIL/USDT"
]

def get_best_symbols(limit=3):
    markets = binance.load_markets()
    candidates = []

    for symbol in STABLE_PAIRS:
        if symbol not in markets:
            continue
        try:
            ohlcv = binance.fetch_ohlcv(symbol, timeframe='1h', limit=1)
            ticker = binance.fetch_ticker(symbol)
            time.sleep(0.2)  # tránh bị block IP

            if not ohlcv or 'percentage' not in ticker or ticker['percentage'] is None:
                continue

            volume = ohlcv[-1][5]
            percent = abs(ticker['percentage'])
            score = volume * percent
            candidates.append((symbol, score))
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu {symbol}: {e}")
            continue

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in candidates[:limit]]

# === Theo dõi và bán coin ===
TIMEFRAME = "5m"
SL_MULTIPLIER = 1.5
TP_MULTIPLIER = 2.0
TRAILING_TRIGGER = 0.5

def calculate_atr(symbol):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=14)
    trs = [abs(c[2] - c[3]) for c in ohlcv[-14:]]
    return sum(trs) / len(trs)

def monitor_price_and_sell(symbol, qty, entry_price, strategy="auto"):
    atr = calculate_atr(symbol)
    sl_price = entry_price - SL_MULTIPLIER * atr
    tp_price = entry_price + TP_MULTIPLIER * atr
    trailing_active = False
    trailing_sl = None

    send_telegram(f"📉 Theo dõi {symbol} – SL: {sl_price:.2f} | TP: {tp_price:.2f}")
    start_time = datetime.now()

    while (datetime.now() - start_time) < timedelta(minutes=5):
        try:
            price = binance.fetch_ticker(symbol)['last']
            ohlcv_data = binance.fetch_ohlcv(symbol, timeframe='5m', limit=50)
            df = pd.DataFrame(ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            market_state = classify_market_state(df)

            if not trailing_active and price >= entry_price + (TP_MULTIPLIER * atr * TRAILING_TRIGGER):
                trailing_active = True
                trailing_sl = price - atr * 0.8
                send_telegram(f"🔁 Trailing Stop kích hoạt tại {price:.2f}")

            if trailing_active and price <= trailing_sl or price >= tp_price or price <= sl_price:
                result = "win" if price >= tp_price or (trailing_active and price <= trailing_sl) else "loss"
                pnl = (price - entry_price) * qty

                binance.create_market_sell_order(symbol, qty)
                send_telegram(f"{'🟢' if result == 'win' else '🔴'} Đã bán {symbol} tại {price:.2f} | PnL: {pnl:.2f} USDT")
                log_to_sheet(symbol, "SELL", qty, price, strategy, result, round(pnl, 2))
                log_strategy(symbol, strategy, result, pnl, market_state)
                return
            time.sleep(10)
        except Exception as e:
            print(f"[Lỗi monitor {symbol}]: {e}")
            time.sleep(5)
