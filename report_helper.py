# report_helper.py

import requests
from datetime import datetime
import builtins
from balance_helper import get_balance, get_used_capital
from config import SHEET_WEBHOOK, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from logger_helper import log_info, log_error

# ✅ Gửi log hằng ngày lên Google Sheet
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
        if SHEET_WEBHOOK:
            requests.post(SHEET_WEBHOOK, json=data)
            log_info("📤 Đã gửi báo cáo vốn hằng ngày lên Google Sheets.")
        else:
            log_error("⚠️ SHEET_WEBHOOK chưa được cấu hình.")
    except Exception as e:
        log_error(f"❌ Lỗi gửi báo cáo vốn: {e}")

# ✅ Gửi báo cáo về Telegram 06:00 sáng
def send_uptime_report():
    try:
        now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        total = get_balance()
        used = get_used_capital()
        cap = builtins.capital_limit
        msg = (
            f"⏰ 06:00 – *Uptime HopperT*\n\n"
            f"• Tổng số dư: {total:.2f} USDT\n"
            f"• Vốn còn lại: {cap:.2f} USDT\n"
            f"• Vốn đã dùng: {used:.2f} USDT\n"
            f"• Trạng thái bot: {'🟢 Chạy' if builtins.bot_active else '🔴 Dừng'}\n\n"
            f"📅 {now}"
        )

        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown"
            }
            requests.post(url, data=data)
            log_info("✅ Đã gửi báo cáo uptime về Telegram.")
        else:
            log_error("⚠️ TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID chưa cấu hình.")
    except Exception as e:
        log_error(f"❌ Lỗi gửi báo cáo uptime: {e}")
