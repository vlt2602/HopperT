import ccxt
import time

# Khởi tạo đối tượng Binance
binance = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 10000
})

# Danh sách các cặp USDT phổ biến để hạn chế API call
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
