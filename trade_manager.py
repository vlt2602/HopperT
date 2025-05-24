# trade_manager.py

from capital_manager import adjust_capital, get_base_capital
import builtins
from telegram_handler import send_alert  # 🆕 Để gửi cảnh báo về Telegram

# 🆕 Khởi tạo biến đếm lỗi toàn cục
error_count = 0
MAX_ERRORS = 3

async def execute_trade(symbol, strategy):
    """
    Hàm xử lý giao dịch thực tế.
    Tích hợp điều chỉnh vốn tự động theo winrate.
    Bắt lỗi mạng/API, tự dừng bot nếu lỗi liên tiếp.
    """
    global error_count
    try:
        # Lấy vốn gốc và điều chỉnh vốn dựa trên winrate
        base_capital = get_base_capital()
        capital_to_use = adjust_capital(symbol, strategy, base_capital)

        if builtins.bot_active:
            # 🔥 Thực hiện giao dịch thực tế (hoặc giả lập)
            print(f"💰 Đặt lệnh {symbol} với {capital_to_use:.2f} USDT theo chiến lược {strategy}")
            # TODO: Tích hợp gọi API Binance nếu muốn thực tế
            builtins.last_order = f"{symbol} | {strategy} | vốn: {capital_to_use:.2f} USDT"
            error_count = 0  # Reset lỗi khi thành công
        else:
            print(f"⏸ Bot đang dừng, bỏ qua giao dịch {symbol}")

    except Exception as e:
        error_count += 1
        print(f"❌ Lỗi execute_trade {symbol}: {e}")
        send_alert(f"⚠️ Lỗi xử lý lệnh {symbol}: {e}")  # Gửi cảnh báo Telegram

        if error_count >= MAX_ERRORS:
            builtins.bot_active = False
            send_alert("🚨 Bot tự động dừng do lỗi liên tiếp!")
