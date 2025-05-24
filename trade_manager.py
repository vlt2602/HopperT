from capital_manager import adjust_capital, get_base_capital
import builtins
from strategy_manager import update_winrate
from logger_helper import log_info, log_error

error_count = 0
MAX_ERRORS = 3

async def execute_trade(symbol, strategy):
    global error_count
    try:
        base_capital = get_base_capital()
        capital_to_use = adjust_capital(symbol, strategy, base_capital)

        if builtins.bot_active:
            if capital_to_use < 10:
                log_error(f"🚨 Tài khoản không đủ USDT để giao dịch {symbol}. Bot sẽ tạm dừng.")
                builtins.bot_active = False
                return

            log_info(f"🚀 Mua {symbol} với {capital_to_use:.2f} USDT theo chiến lược {strategy}")
            import random
            pnl = round(random.uniform(-10, 10), 2)
            result = 1 if pnl > 0 else 0
            update_winrate(symbol, strategy, result)
            builtins.last_order = f"{symbol} | {strategy} | vốn: {capital_to_use:.2f} USDT | PnL: {pnl}"
            error_count = 0
        else:
            log_info(f"⏸ Bot đang dừng, bỏ qua giao dịch {symbol}")
    except Exception as e:
        error_count += 1
        log_error(f"❌ Lỗi execute_trade {symbol}: {e}")
        if error_count >= MAX_ERRORS:
            builtins.bot_active = False
            log_error("🚨 Bot tự động dừng do lỗi liên tiếp!")
