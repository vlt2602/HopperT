# macd_strategy.py (nâng cấp)

def check_macd_signal(df):
    short_ema = df['close'].ewm(span=12).mean()
    long_ema = df['close'].ewm(span=26).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9).mean()
    hist = macd - signal

    # ===== Điều kiện xác nhận nâng cao =====
    condition_1 = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] < signal.iloc[-2]
    condition_2 = macd.iloc[-1] > 0 and signal.iloc[-1] > 0
    condition_3 = hist.iloc[-1] > hist.iloc[-2] and hist.iloc[-1] > 0

    return condition_1 and condition_2 and condition_3
