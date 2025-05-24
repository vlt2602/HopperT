# macd_strategy.py

from logger import log_error

def check_macd_signal(df):
    try:
        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal

        condition_1 = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] < signal.iloc[-2]
        condition_2 = macd.iloc[-1] > 0 and signal.iloc[-1] > 0
        condition_3 = hist.iloc[-1] > hist.iloc[-2] and hist.iloc[-1] > 0

        return condition_1 and condition_2 and condition_3
    except Exception as e:
        log_error(f"❌ Lỗi kiểm tra tín hiệu MACD: {e}")
        return False
