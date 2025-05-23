import time
import ccxt
import builtins
from config import FIXED_USDT_PER_ORDER, BINANCE_API_KEY, BINANCE_SECRET
from logger_helper import send_telegram
from strategy_logger import log_to_sheet, log_strategy

# ✅ Đã đổi sang import từ file riêng
from price_watcher import monitor_price_and_sell

# ✅ Khởi tạo binance đúng API key
from binance_handler import binance

MIN_NOTIONAL = 10

def is_breakout(symbol):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe='5m', limit=6)
        highs = [candle[2] for candle in ohlcv[:-1]]
        current_close = ohlcv[-1][4]
        avg_high = sum(highs) / len(highs)
        return current_close > max(highs) and (current_close - avg_high) / avg_high > 0.01
    except:
        return False

def run_breakout_strategy(strategy_name="breakout"):
    symbols = builtins.TRADE_SYMBOLS if hasattr(builtins, 'TRADE_SYMBOLS') else ["BTC/USDT", "ETH/USDT"]
    for symbol in symbols:
        try:
            balance = binance.fetch_balance()['USDT']['free']
            capital_limit = builtins.capital_limit
            amount_usdt = min(FIXED_USDT_PER_ORDER, capital_limit, balance)

            if amount_usdt < MIN_NOTIONAL:
                send_telegram(f"⚠️ Không đủ USDT để trade {symbol}. Bỏ qua.")
                continue

            if is_breakout(symbol):
                ticker = binance.fetch_ticker(symbol)
                price = ticker['last']
                qty = round(amount_usdt / price, 5)

                binance.create_market_buy_order(symbol, qty)
                entry_price = price

                send_telegram(f"🚀 Breakout Signal! Mua {symbol} {qty} tại {entry_price:.2f}")
                log_to_sheet(symbol, "BUY", qty, entry_price, strategy_name, "pending", 0)
                builtins.capital_limit -= amount_usdt

                monitor_price_and_sell(symbol, qty, entry_price, strategy_name)
                time.sleep(2)

        except Exception as e:
            send_telegram(f"❌ Breakout lỗi {symbol}: {e}")

def check_breakout_signal(df):
    highs = df['high'].tolist()
    closes = df['close'].tolist()
    recent_high = max(highs[-6:])
    recent_close = closes[-1]
    return recent_close >= 0.98 * recent_high
