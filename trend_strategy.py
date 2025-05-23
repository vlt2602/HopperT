def check_trend_signal(df):
    try:
        if df.shape[0] < 50:
            return False  # Không đủ dữ liệu

        df['ema20'] = df['close'].ewm(span=20).mean()
        df['ema50'] = df['close'].ewm(span=50).mean()

        # Nếu EMA20 > EMA50 → có xu hướng tăng
        return df['ema20'].iloc[-1] > df['ema50'].iloc[-1]

    except Exception as e:
        print(f"[Trend Strategy] Lỗi tính tín hiệu trend: {e}")
        return False
