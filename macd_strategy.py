# macd_strategy.py

def check_macd_signal(df):
    try:
        # ✅ Tính MACD theo chuẩn
        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal

        # ===== Điều kiện xác nhận nâng cao =====
        condition_1 = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] < signal.iloc[-2]  # giao cắt lên
        condition_2 = macd.iloc[-1] > 0 and signal.iloc[-1] > 0  # ở vùng dương
        condition_3 = hist.iloc[-1] > hist.iloc[-2] and hist.iloc[-1] > 0  # histogram đang tăng

        return condition_1 and condition_2 and condition_3
    except Exception as e:
        print(f"[MACD] Lỗi kiểm tra tín hiệu: {e}")
        return False
