# report_helper.py

import requests
from datetime import datetime
import builtins
from balance_helper import get_balance, get_used_capital
from config import SHEET_WEBHOOK, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def log_daily_report():
    try:
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_balance": get_balance(),
            "capital_limit": builtins.capital_limit_init,
            "capital_used": get_used_capital(),
            "pnl": round(get_balance() - builtins.capital_limit_init, 2),
            "status": "✅" if builtins.bot_active else "🛑"
        }
        requests.post(SHEET_WEBHOOK, json=data)
        print("📤 Gửi báo cáo vốn hằng ngày lên Google Sheets.")
    except Exception as e:
        print("❌ Lỗi gửi báo cáo:", e)


def send_uptime_report():
    try:
        now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        total = get_balance()
        used = get_used_capital()
        cap = builtins.capital_limit
        msg = (
            f"⏰ 06:00 – *Uptime HopperX*\n\n"
            f"• Tổng số dư: {total:.2f} USDT\n"
            f"• Vốn còn lại: {cap:.2f} USDT\n"
            f"• Vốn đã dùng: {used:.2f} USDT\n"
            f"• Trạng thái bot: {'🟢 Chạy' if builtins.bot_active else '🔴 Dừng'}\n\n"
            f"📅 {now}")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data)
        print("✅ Đã gửi báo cáo uptime 06:00 sáng.")
    except Exception as e:
        print("❌ Lỗi gửi báo cáo uptime:", e)
