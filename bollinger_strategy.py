# bollinger_strategy.py

from logger_helper import log_info, log_error

def check_bollinger_signal(df):
    try:
        if len(df) < 22:
            return False  # Cần đủ dữ liệu để tính BB (20 cây + buffer)

        close = df['close']
        open_ = df['open']

        ma = close.rolling(window=20).mean()
        std = close.rolling(window=20).std()
        upper = ma + 2 * std
        lower = ma - 2 * std

        close_prev = close.iloc[-2]
        close_now = close.iloc[-1]
        open_now = open_.iloc[-1]
        lower_prev = lower.iloc[-2]
        lower_now = lower.iloc[-1]

        condition_1 = close_prev < lower_prev
        condition_2 = close_now > open_now
        condition_3 = close_now < lower_now * 1.01

        return condition_1 and condition_2 and condition_3
    except Exception as e:
        log_error(f"❌ Lỗi check_bollinger_signal: {e}")
        return False
