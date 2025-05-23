import ccxt
import time

def get_best_symbols(limit=5):
    exchange = ccxt.binance()
    markets = exchange.load_markets()

    candidates = []

    for symbol in markets:
        if "/USDT" not in symbol:
            continue
        if not markets[symbol].get('active', False):
            continue

        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=1)
            if not ohlcv:
                continue
            volume = ohlcv[-1][5]  # cột volume
            ticker = exchange.fetch_ticker(symbol)
            percent = abs(ticker.get('percentage', 0))
            score = volume * percent
            candidates.append((symbol, score))
        except:
            continue

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [s[0].replace("/", "") for s in candidates[:limit]]

if __name__ == "__main__":
    print("Top coin đề xuất:")
    for sym in get_best_symbols():
        print("-", sym)
