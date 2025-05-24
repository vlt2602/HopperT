import json
from datetime import datetime
import os
from logger import log_info

winrate_file = "winrate_log.json"

def load_winrate():
    try:
        if not os.path.exists(winrate_file):
            return {}
        with open(winrate_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_info(f"Lỗi load_winrate: {e}")
        return {}

def save_winrate(data):
    try:
        with open(winrate_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        log_info(f"Lỗi save_winrate: {e}")

def update_winrate(symbol, strategy, result):  # result: 1 thắng, 0 thua
    data = load_winrate()
    key = f"{symbol}_{strategy}"
    if key not in data:
        data[key] = {"win": 0, "total": 0, "last_update": str(datetime.now())}
    data[key]["win"] += result
    data[key]["total"] += 1
    data[key]["last_update"] = str(datetime.now())
    save_winrate(data)

def check_winrate(symbol, strategy):
    data = load_winrate()
    key = f"{symbol}_{strategy}"
    if key not in data or data[key]["total"] < 5:  # ít nhất 5 lệnh mới đánh giá
        return 50  # Tạm cho winrate 50%
    win = data[key]["win"]
    total = data[key]["total"]
    return (win / total) * 100

def get_next_strategy(current_strategy):
    strategies = ["breakout", "vwap", "reversal", "macd"]
    idx = strategies.index(current_strategy)
    return strategies[(idx + 1) % len(strategies)]

def get_best_strategy():
    data = load_winrate()
    strategy_scores = {}
    for key, value in data.items():
        strategy = key.split("_")[1]
        total = value["total"]
        winrate = (value["win"] / total) * 100 if total > 0 else 0
        if strategy not in strategy_scores:
            strategy_scores[strategy] = {"win": value["win"], "total": total}
        else:
            strategy_scores[strategy]["win"] += value["win"]
            strategy_scores[strategy]["total"] += total
    if not strategy_scores:
        return "breakout"  # Mặc định nếu chưa có dữ liệu
    best_strategy = max(strategy_scores.items(), key=lambda x: (x[1]["win"] / x[1]["total"]) if x[1]["total"] > 0 else 0)
    return best_strategy[0]

def get_best_symbols():
    # 🆕 Hàm giả định để lấy danh sách symbol tốt nhất (có thể dùng phân tích thị trường thực tế)
    return ["SHIB/USDT", "DOGE/USDT", "ADA/USDT"]
