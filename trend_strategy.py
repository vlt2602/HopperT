from logger_helper import log_info, log_error

def check_trend_signal(df):
    try:
        if df.shape[0] < 50:
            return False  # Không đủ dữ liệu

        df['ema20'] = df['close'].ewm(span=20).mean()
        df['ema50'] = df['close'].ewm(span=50).mean()

        return df['ema20'].iloc[-1] > df['ema50'].iloc[-1]
    except Exception as e:
        log_error(f"❌ Lỗi tính tín hiệu trend: {e}")
        return False
