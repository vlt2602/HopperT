import ccxt
import time

def get_best_symbols(limit=5):
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    tickers = exchange.fetch_tickers()

    candidates = []

    for symbol, data in tickers.items():
        if "/USDT" not in symbol:
            continue
        if symbol not in markets:
            continue
        info = markets[symbol]
        if not info.get('active', False):
            continue
        vol = data.get('quoteVolume', 0)
        percent = abs(data.get('percentage', 0))
        if vol and percent:
            score = vol * percent  # volume * biến động
            candidates.append((symbol, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [s[0].replace("/", "") for s in candidates[:limit]]

if __name__ == "__main__":
    print("Top coin đề xuất:")
    for sym in get_best_symbols():
        print("-", sym)
