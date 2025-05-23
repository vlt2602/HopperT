# rsi_strategy.py

import time
import ccxt
import builtins
from config import FIXED_USDT_PER_ORDER, BINANCE_API_KEY, BINANCE_SECRET
from logger_helper import send_telegram
from strategy_logger import log_to_sheet, log_strategy
from indicator_helper import calculate_rsi
from price_watcher import monitor_price_and_sell  # ✅ Sửa lại đúng file

# ✅ Khởi tạo kết nối Binance
binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True
})

MIN_NOTIONAL = 10

# ✅ Check tín hiệu RSI trực tiếp từ thị trường
def is_rsi_reversal(symbol):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe='15m', limit=100)
        closes = [c[4] for c in ohlcv]
        rsi = calculate_rsi(closes)
        return rsi < 30
    except:
        return False

# ✅ Chạy chiến lược RSI
def run_rsi_strategy(strategy_name="rsi"):
    symbols = getattr(builtins, 'TRADE_SYMBOLS', ["BTC/USDT", "ETH/USDT"])
    for symbol in symbols:
        try:
            balance = binance.fetch_balance()['USDT']['free']
            capital_limit = getattr(builtins, 'capital_limit', balance)
            amount_usdt = min(FIXED_USDT_PER_ORDER, capital_limit, balance)

            if amount_usdt < MIN_NOTIONAL:
                continue

            if is_rsi_reversal(symbol):
                price = binance.fetch_ticker(symbol)['last']
                qty = round(amount_usdt / price, 5)
                binance.create_market_buy_order(symbol, qty)

                send_telegram(f"🔄 RSI Reversal! Mua {symbol} {qty} tại {price:.2f}")
                log_to_sheet(symbol, "BUY", qty, price, strategy_name, "pending", 0)
                builtins.capital_limit -= amount_usdt

                monitor_price_and_sell(symbol, qty, price, strategy_name)
                time.sleep(2)

        except Exception as e:
            send_telegram(f"❌ RSI lỗi {symbol}: {e}")
