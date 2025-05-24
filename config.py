# config.py

import os

# 🔐 Thông tin bảo mật từ biến môi trường
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET_KEY")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
ALLOWED_CHAT_ID = TELEGRAM_CHAT_ID  # chặn người lạ

# ⚙️ Cài đặt chiến lược và vốn
TRADE_SYMBOLS = ["ETH/USDT", "BTC/USDT"]  # fallback nếu không có phân tích thị trường
TRADE_PERCENT = 0.05  # fallback nếu không dùng vốn cố định

USE_FIXED_CAPITAL = True
FIXED_USDT_PER_ORDER = 15

# 💰 Giới hạn vốn đầu tư
USE_CAPITAL_LIMIT = True
CAPITAL_LIMIT = 500

# 📊 Ghi log Google Sheet (có thể bật nếu cần)
USE_GOOGLE_SHEET = True  # 🆕 Kích hoạt ghi log Google Sheets
SHEET_WEBHOOK = "https://script.google.com/macros/s/AKfycbxi3W8SK9HMOJicjTvka9HCxvPC17HPWKpwFGa6MDT9KCqZsRyUMDoq1M_oa9GZV_LTSQ/exec"

# 🛑 Dừng lỗ tối đa theo ngày
DAILY_MAX_LOSS = -30  # cho phép lỗ tối đa 30 USDT/ngày
