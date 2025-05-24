# balance_helper.py

import builtins
from config import CAPITAL_LIMIT
from binance_handler import binance  # ✅ import chuẩn đã có apiKey

# ✅ Biến khởi tạo ban đầu
builtins.capital_limit_init = CAPITAL_LIMIT
builtins.capital_limit = CAPITAL_LIMIT

def get_balance():
    try:
        return round(binance.fetch_balance()['USDT']['free'], 2)
    except Exception as e:
        print(f"[Lỗi lấy balance]: {e}")
        return 0.0

def get_used_capital():
    try:
        return round(builtins.capital_limit_init - builtins.capital_limit, 2)
    except:
        return 0.0
