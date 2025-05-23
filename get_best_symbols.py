import ccxt
import time

# Danh sách các cặp USDT phổ biến để hạn chế API call
STABLE_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "DOT/USDT", "AVAX/USDT",
    "SHIB/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "TRX/USDT",
    "LINK/USDT", "ATOM/USDT", "APT/USDT", "NEAR/USDT", "FIL/USDT"
]

def get_best_symbols(limit=3):
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    candidates = []

    for symbol in STABLE_PAIRS:
        if symbol not in markets:
            continue
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=1)
            ticker = exchange.fetch_ticker(symbol)
            time.sleep(0.2)  # tránh bị block IP

            if not ohlcv or 'percentage' not in ticker:
                continue

            volume = ohlcv[-1][5]
            percent = abs(ticker['percentage'])
            score = volume * percent
            candidates.append((symbol, score))

        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu {symbol}: {e}")
            continue

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [s[0].replace("/", "") for s in candidates[:limit]]

if __name__ == "__main__":
    print("Top coin đề xuất:")
    for sym in get_best_symbols():
        print("-", sym)
