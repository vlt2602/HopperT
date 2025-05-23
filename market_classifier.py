# market_classifier.py
def classify_market_state(df):
    closes = df['close']
    highs = df['high']
    lows = df['low']
    range_ = highs.max() - lows.min()
    body_avg = (highs - lows).mean()

    if range_ > body_avg * 3:
        return "trend"
    elif range_ < body_avg * 1.5:
        return "sideway"
    else:
        return "unclear"
