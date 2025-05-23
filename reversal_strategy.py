from indicator_helper import calculate_rsi  # dùng chung hàm RSI

def check_reversal_signal(df, period=14):
    close = df['close']
    recent_rsi = calculate_rsi(close.tolist(), period=period)

    # Đảo chiều giảm nếu RSI quá cao (quá mua)
    return recent_rsi > 70
