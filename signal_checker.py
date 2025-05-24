from indicator_helper import calculate_rsi
from logger_helper import log_info, log_error

def check_rsi_signal(df):
    try:
        close_prices = df['close'].tolist()
        rsi = calculate_rsi(close_prices)
        return rsi < 35  # Tín hiệu mua khi quá bán
    except Exception as e:
        log_error(f"❌ Lỗi check_rsi_signal: {e}")
        return False
