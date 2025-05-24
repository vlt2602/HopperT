# ai_strategy.py

import pandas as pd
from strategy_metrics import get_strategy_scores, predict_best_strategy
from signal_checker import check_rsi_signal
from breakout_strategy import check_breakout_signal
from scalping_strategy import check_scalping_signal
from trend_strategy import check_trend_signal
from reversal_strategy import check_reversal_signal
from macd_strategy import check_macd_signal
from bollinger_strategy import check_bollinger_signal
from vwap_strategy import check_vwap_signal
from indicator_helper import calculate_rsi
from binance_handler import binance
from logger_helper import log_info, log_error

# ✅ TỰ CHỌN CHIẾN LƯỢC TỐI ƯU THEO AI + HIỆU SUẤT + THỊ TRƯỜNG
def select_strategy(df):
    scores = get_strategy_scores(days=7)
    if not scores:
        return "breakout"

    market_state = classify_market_state(df)
    log_info(f"📈 Phân loại thị trường hiện tại: {market_state}")

    strat_ranked = []
    for name, data in scores.items():
        market_pnl = data.get("by_market", {}).get(market_state, -9999)
        strat_ranked.append((name, market_pnl))

    strat_ranked = sorted(strat_ranked, key=lambda x: x[1], reverse=True)
    best_for_market = strat_ranked[0][0] if strat_ranked else "breakout"

    signal_checks = {
        "trend": check_trend_signal(df),
        "scalping": check_scalping_signal(df),
        "breakout": check_breakout_signal(df),
        "rsi": check_rsi_signal(df),
        "macd": check_macd_signal(df),
        "bollinger": check_bollinger_signal(df),
        "vwap": check_vwap_signal(df)
    }

    if signal_checks.get(best_for_market):
        log_info(f"✅ Chọn chiến lược {best_for_market} do có tín hiệu kỹ thuật.")
        return best_for_market

    valid = {
        name: data for name, data in scores.items()
        if data["winrate"] >= 40 and data["pnl"] > 0
    }

    preferred = sorted(valid.items(), key=lambda x: x[1]["score"], reverse=True)
    if preferred:
        chosen = preferred[0][0]
        log_info(f"✅ Chọn chiến lược fallback: {chosen}")
        return chosen
    else:
        try:
            rsi_value = calculate_rsi(df["close"].tolist())
            volume_now = df["volume"].iloc[-1]
            predicted = predict_best_strategy(market_state, rsi_value, volume_now)
            log_info(f"✅ Chọn chiến lược dự đoán: {predicted}")
            return predicted
        except Exception as e:
            log_error(f"❌ Lỗi chọn fallback chiến lược: {e}")
            return "breakout"

# ✅ PHÂN LOẠI TRẠNG THÁI THỊ TRƯỜNG: Trend / Sideway / Volatile
def classify_market_state(df):
    try:
        df['ema20'] = df['close'].ewm(span=20).mean()
        df['ema50'] = df['close'].ewm(span=50).mean()
        df['returns'] = df['close'].pct_change()
        df['rsi'] = calculate_rsi(df['close'].tolist(), period=14)
        volatility = df['returns'].rolling(window=10).std().iloc[-1]
        ema_diff = df['ema20'].iloc[-1] - df['ema50'].iloc[-1]
        volume_now = df['volume'].iloc[-1]
        volume_avg = df['volume'].rolling(window=10).mean().iloc[-1]

        if ema_diff > 0.5 and volatility < 0.015 and df['rsi'].iloc[-1] > 55 and volume_now > volume_avg:
            return "trend"
        if abs(ema_diff) < 0.2 and volatility < 0.008 and 45 <= df['rsi'].iloc[-1] <= 55:
            return "sideway"
        return "volatile"
    except Exception as e:
        log_error(f"❌ Lỗi classify_market_state: {e}")
        return "volatile"

# ✅ TỰ CHỌN TIMEFRAME: 1m / 5m / 15m theo độ biến động
def select_timeframe(symbol):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe="15m", limit=30)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df['returns'] = df['close'].pct_change()
        volatility = df['returns'].rolling(window=10).std().iloc[-1]

        if volatility > 0.015:
            return "1m"
        elif volatility > 0.007:
            return "5m"
        else:
            return "15m"
    except Exception as e:
        log_error(f"❌ Lỗi select_timeframe: {e}")
        return "5m"
