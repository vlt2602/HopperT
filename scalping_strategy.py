# scalping_strategy.py

from logger import log_error

def check_scalping_signal(df):
    try:
        closes = df['close'].tolist()
        recent = closes[-4:]
        volatility = max(recent) - min(recent)
        return volatility / recent[-1] > 0.015
    except Exception as e:
        log_error(f"❌ Lỗi check_scalping_signal: {e}")
        return False
