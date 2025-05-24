# vwap_strategy.py (nâng cấp)


def check_vwap_signal(df):
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["cum_tp_vol"] = (df["typical_price"] * df["volume"]).cumsum()
    df["cum_vol"] = df["volume"].cumsum()
    df["vwap"] = df["cum_tp_vol"] / df["cum_vol"]

    close = df["close"]
    vwap = df["vwap"]
    volume = df["volume"]

    # ===== Xác nhận tín hiệu nâng cao =====
    cross_up = close.iloc[-2] < vwap.iloc[-2] and close.iloc[-1] > vwap.iloc[-1]
    breakout_strength = (close.iloc[-1] -
                         vwap.iloc[-1]) / vwap.iloc[-1] > 0.003
    volume_ok = volume.iloc[-1] >= volume.iloc[-10:-1].mean()

    return cross_up and breakout_strength and volume_ok
