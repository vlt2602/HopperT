import pandas as pd
from datetime import datetime, timedelta


# ✅ Đọc file log & xử lý bằng pandas
def read_log():
    try:
        df = pd.read_csv("strategy_log.csv",
                         header=None,
                         names=["time", "symbol", "strategy", "result", "pnl"])
        df["time"] = pd.to_datetime(df["time"])
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
        df = df.dropna(subset=["pnl"])  # loại dòng lỗi
        return df
    except Exception as e:
        print(f"Lỗi đọc strategy_log.csv: {e}")
        return pd.DataFrame()


# ✅ Tính hiệu suất từng chiến lược
def get_strategy_scores(days=7):
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    try:
        df = pd.read_csv("strategy_log.csv",
                         header=None,
                         names=[
                             "time", "symbol", "strategy", "market_state",
                             "result", "pnl"
                         ])
    except Exception as e:
        print(f"Lỗi đọc strategy_log.csv: {e}")
        return {}

    df["time"] = pd.to_datetime(df["time"])
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
    df = df.dropna(subset=["pnl"])
    df = df[df["time"] >= cutoff]

    if df.empty:
        return {}

    data = {}
    for strat in df["strategy"].unique():
        strat_df = df[df["strategy"] == strat]
        wins = (strat_df["result"] == "win").sum()
        losses = (strat_df["result"] == "loss").sum()
        pnl = strat_df["pnl"].sum()
        count = len(strat_df)
        winrate = wins / count if count > 0 else 0
        score = (winrate * 100) * pnl

        # Phân nhóm theo trạng thái thị trường
        by_state = strat_df.groupby("market_state")["pnl"].sum().to_dict()

        data[strat] = {
            "score": round(score, 2),
            "winrate": round(winrate * 100, 1),
            "pnl": round(pnl, 2),
            "by_market": by_state  # ← hiệu suất theo thị trường
        }

    return data


# ✅ Dùng để tính vốn động theo chiến lược
def get_dynamic_usdt_allocation(strategy_name, base_amount=15):
    scores = get_strategy_scores(days=7)
    if strategy_name not in scores:
        return base_amount
    winrate = scores[strategy_name]["winrate"]
    if winrate > 80:
        return round(base_amount * 2, 2)
    elif winrate > 70:
        return round(base_amount * 1.5, 2)
    else:
        return base_amount


# ✅ Tối ưu vốn theo winrate chiến lược
# strategy_metrics.py (nâng cấp phần cuối)


def get_optimal_usdt_amount(strategy_name, base_usdt=15):
    scores = get_strategy_scores(days=7)
    if strategy_name not in scores:
        return base_usdt

    winrate = scores[strategy_name]['winrate']
    pnl = scores[strategy_name]['pnl']

    # Mặc định: giữ nguyên
    multiplier = 1.0

    if winrate > 75:
        multiplier = 2.0
    elif winrate > 60:
        multiplier = 1.5
    elif winrate < 40 or pnl < 0:
        multiplier = 0.8  # Giảm vốn nếu hiệu suất kém

    # Nếu chiến lược tốt và gần đây có chuỗi thắng → bonus thêm
    bonus = 1.1 if winrate > 70 and pnl > 10 else 1.0

    return round(base_usdt * multiplier * bonus, 2)
def predict_best_strategy(current_state: str, current_rsi: float, current_volume: float):
    try:
        df = pd.read_csv("strategy_log.csv", header=None,
                         names=["time", "symbol", "strategy", "market_state", "result", "pnl"])
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
        df = df.dropna(subset=["pnl"])
        df = df[df["pnl"] > 0]  # chỉ lấy các giao dịch có lãi
        df = df[df["market_state"] == current_state]

        if df.empty:
            return "breakout"  # fallback nếu không đủ dữ liệu

        # Đếm số lần mỗi chiến lược thành công theo market_state
        strat_stats = df.groupby("strategy")["pnl"].agg(["count", "sum"]).sort_values(by="sum", ascending=False)

        best_strategy = strat_stats.index[0]
        return best_strategy
    except Exception as e:
        print(f"[AI Predict] Lỗi phân tích chiến lược: {e}")
        return "breakout"
