# binance_handler.py

import ccxt
import time
from config import BINANCE_API_KEY, BINANCE_SECRET
from logger_helper import log_error

# ✅ Khởi tạo kết nối Binance duy nhất có API key
binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'timeout': 10000
})

# ✅ Danh sách các cặp USDT phổ biến (lọc trước để tránh gọi quá nhiều)
STABLE_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "DOT/USDT", "AVAX/USDT",
    "SHIB/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "TRX/USDT",
    "LINK/USDT", "ATOM/USDT", "APT/USDT", "NEAR/USDT", "FIL/USDT"
]

# ✅ Lọc top coin tốt nhất theo volume * biến động %
def get_best_symbols(limit=3):
    try:
        markets = binance.load_markets()
    except Exception as e:
        log_error(f"❌ Lỗi load markets: {e}")
        return []

    candidates = []

    for symbol in STABLE_PAIRS:
        if symbol not in markets:
            continue
        try:
            ohlcv = binance.fetch_ohlcv(symbol, '1h', 1)
            ticker = binance.fetch_ticker(symbol)
            time.sleep(0.2)  # tránh bị block IP

            if not ohlcv or 'percentage' not in ticker or ticker['percentage'] is None:
                continue

            volume = ohlcv[-1][5]
            percent = abs(ticker['percentage'])
            score = volume * percent
            candidates.append((symbol, score))

        except Exception as e:
            log_error(f"⚠️ Lỗi dữ liệu {symbol}: {e}")
            continue

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in candidates[:limit]]
