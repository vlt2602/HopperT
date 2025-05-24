from indicator_helper import calculate_rsi
from logger_helper import log_info, log_error

def check_reversal_signal(df, period=14):
    try:
        close = df['close']
        recent_rsi = calculate_rsi(close.tolist(), period=period)
        return recent_rsi > 70  # Đảo chiều giảm nếu RSI quá cao (quá mua)
    except Exception as e:
        log_error(f"❌ Lỗi check_reversal_signal: {e}")
        return False
