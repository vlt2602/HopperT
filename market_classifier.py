# market_classifier.py

def classify_market_state(df):
    try:
        closes = df['close']
        highs = df['high']
        lows = df['low']
        volumes = df['volume']

        range_ = highs.max() - lows.min()
        avg_body = (highs - lows).mean()
        volatility = closes.pct_change().rolling(window=10).std().iloc[-1]
        volume_now = volumes.iloc[-1]
        volume_avg = volumes.rolling(window=10).mean().iloc[-1]

        # ===== THỊ TRƯỜNG CÓ XU HƯỚNG MẠNH (Trend) =====
        if range_ > avg_body * 2.5 and volatility > 0.01 and volume_now > volume_avg:
            return "trend"

        # ===== SIDEWAY (ít biến động, biên hẹp) =====
        if range_ < avg_body * 1.2 and volatility < 0.008:
            return "sideway"

        # ===== KHÓ XÁC ĐỊNH / DAO ĐỘNG MẠNH (Biến động cao) =====
        return "volatile"
    except Exception as e:
        print(f"[Classifier] Lỗi xác định thị trường: {e}")
        return "unclear"
