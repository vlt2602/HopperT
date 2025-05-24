# strategy_manager.py
import json
from datetime import datetime, timedelta

winrate_file = "winrate_log.json"

def load_winrate():
    try:
        with open(winrate_file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_winrate(data):
    with open(winrate_file, 'w') as f:
        json.dump(data, f)

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
