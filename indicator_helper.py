# indicator_helper.py

from logger_helper import log_info, log_error

def calculate_rsi(prices, period=14):
    try:
        if len(prices) < period + 1:
            return 50  # fallback trung tính nếu không đủ dữ liệu

        deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
        gains = [max(delta, 0) for delta in deltas]
        losses = [abs(min(delta, 0)) for delta in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(deltas)):
            gain = gains[i]
            loss = losses[i]
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            return 100  # RSI tối đa nếu không có lỗ

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except Exception as e:
        log_error(f"❌ Lỗi tính RSI: {e}")
        return 50
