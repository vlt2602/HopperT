# balance_helper.py

import ccxt
from config import BINANCE_API_KEY, BINANCE_SECRET, CAPITAL_LIMIT
import builtins

# ✅ Khởi tạo kết nối Binance riêng
binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True
})

# ✅ Biến khởi tạo ban đầu
builtins.capital_limit_init = CAPITAL_LIMIT
builtins.capital_limit = CAPITAL_LIMIT


def get_balance():
    try:
        return round(binance.fetch_balance()['USDT']['free'], 2)
    except:
        return 0.0


def get_used_capital():
    try:
        return round(builtins.capital_limit_init - builtins.capital_limit, 2)
    except:
        return 0.0
