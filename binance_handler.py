import ccxt, time
from datetime import datetime, timedelta
from config import (BINANCE_API_KEY, BINANCE_SECRET, TRADE_SYMBOLS,
                    TRADE_PERCENT, USE_FIXED_CAPITAL, FIXED_USDT_PER_ORDER,
                    CAPITAL_LIMIT, USE_CAPITAL_LIMIT, DAILY_MAX_LOSS)
from logger_helper import send_telegram
from strategy_logger import log_to_sheet, log_strategy
import builtins
from strategy_metrics import get_dynamic_usdt_allocation
from get_best_symbols import get_best_symbols

# Trạng thái toàn cục
builtins.capital_limit = CAPITAL_LIMIT
builtins.capital_limit_init = CAPITAL_LIMIT
builtins.smart_pause = False
builtins.loss_log = []
builtins.daily_loss = 0
builtins.last_reset_day = datetime.now().date()

panic_mode = False
loss_streak = 0

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'timeout': 10000
})

MIN_NOTIONAL = 10
TIMEFRAME = '5m'
SL_MULTIPLIER = 1.5
TP_MULTIPLIER = 2.0
TRAILING_TRIGGER = 0.5

def calculate_atr(symbol):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=14)
    trs = [abs(c[2] - c[3]) for c in ohlcv[-14:]]
    return sum(trs) / len(trs)

def monitor_price_and_sell(symbol, qty, entry_price, strategy="auto"):
    global panic_mode, loss_streak
    atr = calculate_atr(symbol)
    sl_price = entry_price - SL_MULTIPLIER * atr
    tp_price = entry_price + TP_MULTIPLIER * atr
    trailing_active = False
    trailing_sl = None

    send_telegram(f"🎯 Theo dõi {symbol} – SL: {sl_price:.2f} | TP: {tp_price:.2f}")
    start_time = datetime.now()

    while (datetime.now() - start_time) < timedelta(minutes=5):
        try:
            price = binance.fetch_ticker(symbol)['last']
            from ai_strategy import classify_market_state
            ohlcv_data = binance.fetch_ohlcv(symbol, timeframe='5m', limit=50)
            import pandas as pd
            df_log = pd.DataFrame(ohlcv_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            market_state = classify_market_state(df_log)

            if not trailing_active and price >= entry_price + (TP_MULTIPLIER * atr * TRAILING_TRIGGER):
                trailing_active = True
                trailing_sl = price - atr * 0.8
                send_telegram(f"🔁 Trailing Stop kích hoạt tại {price:.2f}")

            if trailing_active and price <= trailing_sl or price >= tp_price or price <= sl_price:
                result = "win" if price >= tp_price or (trailing_active and price <= trailing_sl) else "loss"
                pnl = (price - entry_price) * qty
                loss_streak = 0 if result == "win" else loss_streak + 1

                if loss_streak >= 3:
                    panic_mode = True
                    send_telegram("🛑 DỪNG KHẨN: Lỗ 3 lệnh liên tiếp. Gõ /resume để tiếp tục.")

                binance.create_market_sell_order(symbol, qty)
                send_telegram(f"{'🟢' if result == 'win' else '🔴'} Đã bán tại {price:.2f} | PnL: {pnl:.2f} USDT")
                log_to_sheet(symbol, "SELL", qty, price, strategy, result, round(pnl, 2), market_state)
                log_strategy(symbol, strategy, result, pnl, market_state)
                builtins.capital_limit += pnl

                today = datetime.now().date()
                if today != builtins.last_reset_day:
                    builtins.daily_loss = pnl
                    builtins.last_reset_day = today
                else:
                    builtins.daily_loss += pnl

                if builtins.daily_loss <= DAILY_MAX_LOSS:
                    panic_mode = True
                    send_telegram(f"🚫 Đạt ngưỡng lỗ ngày {builtins.daily_loss:.2f} USDT → Dừng bot.")

                builtins.loss_log.append((datetime.now(), result))
                builtins.loss_log = [x for x in builtins.loss_log if (datetime.now() - x[0]).seconds < 3600]
                recent_losses = sum(1 for _, r in builtins.loss_log if r == "loss")
                if recent_losses >= 2 and not builtins.smart_pause:
                    builtins.smart_pause = True
                    send_telegram("⏸ Nghỉ 30 phút vì thua liên tiếp 2 lệnh.")
                return
            time.sleep(10)
        except Exception as e:
            print(f"[Lỗi monitor {symbol}]: {e}")
            time.sleep(5)

def auto_trade_loop(strategy_name="auto"):
    global panic_mode
    while True:
        if panic_mode:
            print("🛑 Bot PANIC – Dừng giao dịch.")
            time.sleep(60)
            continue

        if builtins.smart_pause:
            print("⏸ Bot đang nghỉ thông minh – chờ 30 phút.")
            time.sleep(1800)
            builtins.smart_pause = False
            builtins.loss_log.clear()
            send_telegram("✅ Hết thời gian nghỉ, tiếp tục giao dịch.")
            continue

        for symbol in get_best_symbols():
            try:
                balance = binance.fetch_balance()['USDT']['free']
                if USE_CAPITAL_LIMIT:
                    capital_available = builtins.capital_limit
                    scaled_amount = get_dynamic_usdt_allocation(strategy_name, base_amount=FIXED_USDT_PER_ORDER)
                    amount_usdt = min(scaled_amount, capital_available, balance)
                else:
                    amount_usdt = min(FIXED_USDT_PER_ORDER, balance)

                if amount_usdt < MIN_NOTIONAL:
                    print(f"[BỎ QUA] {symbol} – {amount_usdt:.2f} USDT không đủ lệnh.")
                    continue

                price = binance.fetch_ticker(symbol)['last']
                qty = round(amount_usdt / price, 5)
                binance.create_market_buy_order(symbol, qty)

                send_telegram(f"✅ Đã mua {symbol} {qty} ({amount_usdt:.2f} USDT) tại giá {price:.2f}")
                log_to_sheet(symbol, "BUY", qty, price, strategy_name, "pending", 0)
                builtins.capital_limit -= amount_usdt

                monitor_price_and_sell(symbol, qty, price, strategy=strategy_name)
                time.sleep(2)

            except Exception as e:
                send_telegram(f"❌ Lỗi xử lý {symbol}: {e}")
        time.sleep(60)
