# indicator_helper.py

def calculate_rsi(prices, period=14):
    deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(deltas)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    rs = avg_gain / avg_loss if avg_loss > 0 else 999
    rsi = 100 - (100 / (1 + rs))
    return rsi
