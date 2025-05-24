# bollinger_strategy.py

def check_bollinger_signal(df):
    if len(df) < 22:
        return False  # Cần đủ dữ liệu để tính BB (20 cây + buffer)

    close = df['close']
    open_ = df['open']

    ma = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    upper = ma + 2 * std
    lower = ma - 2 * std

    # ===== Điều kiện xác nhận nâng cao =====
    close_prev = close.iloc[-2]
    close_now = close.iloc[-1]
    open_now = open_.iloc[-1]
    lower_prev = lower.iloc[-2]
    lower_now = lower.iloc[-1]

    # 1. Giá đóng cửa trước đó dưới dải dưới
    condition_1 = close_prev < lower_prev

    # 2. Nến hiện tại là nến tăng (bullish)
    condition_2 = close_now > open_now

    # 3. Giá vẫn ở gần dải dưới (tránh mua khi giá đã bật quá mạnh)
    condition_3 = close_now < lower_now * 1.01

    return condition_1 and condition_2 and condition_3
