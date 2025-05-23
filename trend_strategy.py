# trend_strategy.py

def check_trend_signal(df):
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()

    # Nếu EMA20 > EMA50 → có xu hướng tăng
    return df['ema20'].iloc[-1] > df['ema50'].iloc[-1]
