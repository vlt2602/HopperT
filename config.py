<<<<<<< HEAD
# config.py

import os

# 🔐 Thông tin bảo mật từ biến môi trường
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET_KEY")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
ALLOWED_CHAT_ID = TELEGRAM_CHAT_ID  # chặn người lạ

# ⚙️ Cài đặt chiến lược và vốn
TRADE_SYMBOLS = ["ETH/USDT", "BTC/USDT"]
TRADE_PERCENT = 0.05  # fallback nếu không dùng vốn cố định

USE_FIXED_CAPITAL = True
FIXED_USDT_PER_ORDER = 15

# 💰 Giới hạn vốn đầu tư
USE_CAPITAL_LIMIT = True
CAPITAL_LIMIT = 500

# 📊 Ghi log Google Sheet (chưa bật)
USE_GOOGLE_SHEET = False
SHEET_WEBHOOK = ""

# 🛑 Dừng lỗ tối đa theo ngày
DAILY_MAX_LOSS = -30  # cho phép lỗ tối đa 30 USDT/ngày
=======
TELEGRAM_TOKEN = "7951632552:AAFOBdhFlEW3HafWCzi6-Us0uSUkIKhM4TI"
ALLOWED_CHAT_ID = 1291424537
>>>>>>> 5a8f10b (Update telegram_handler.py với menu inline mới)
