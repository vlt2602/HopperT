import pandas as pd
from datetime import datetime
import builtins
from logger_helper import send_telegram
from config import DAILY_MAX_LOSS  # ✅ dùng từ config chuẩn

def check_daily_loss():
    try:
        df = pd.read_csv("strategy_log.csv", header=None,
                         names=["time", "symbol", "strategy", "market_state", "result", "pnl"])
        df["time"] = pd.to_datetime(df["time"])
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
        today = datetime.now().strftime("%Y-%m-%d")
        df_today = df[df["time"].dt.strftime("%Y-%m-%d") == today]

        pnl_today = df_today["pnl"].sum()

        if pnl_today <= DAILY_MAX_LOSS:
            if not getattr(builtins, "panic_mode", False):
                builtins.panic_mode = True
                send_telegram(f"🚨 DỪNG KHẨN CẤP: Lỗ hôm nay {pnl_today:.2f} USDT ➜ vượt ngưỡng {DAILY_MAX_LOSS} USDT")
                print("🚨 Kích hoạt panic_mode do lỗ vượt ngưỡng.")
        return pnl_today
    except Exception as e:
        print(f"[risk_manager] Lỗi kiểm tra daily loss: {e}")
        return 0
