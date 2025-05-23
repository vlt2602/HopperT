# scalping_strategy.py


def check_scalping_signal(df):
    # Tín hiệu scalping đơn giản: giá biến động mạnh trong 3 nến gần nhất
    closes = df['close'].tolist()
    recent = closes[-4:]
    volatility = max(recent) - min(recent)

    # Nếu biến động > 1.5% giá → cho là có cơ hội scalping
    return volatility / recent[-1] > 0.015
