# reversal_strategy.py


def check_reversal_signal(df):
    close = df['close']
    recent_rsi = calculate_rsi(close.tolist())

    # Nếu RSI > 70 → cảnh báo đảo chiều giảm
    return recent_rsi > 70


# Cần kèm theo hàm tính RSI đơn giản
def calculate_rsi(prices, period=14):
    deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
