from capital_manager import adjust_capital, get_base_capital
import builtins
from strategy_manager import update_winrate  # 🆕 Bổ sung để tự học winrate

error_count = 0
MAX_ERRORS = 3

async def execute_trade(symbol, strategy):
    """
    Hàm xử lý giao dịch thực tế.
    Tích hợp điều chỉnh vốn tự động theo winrate.
    Ghi log kết quả để AI tự học và tối ưu chiến lược.
    Bắt lỗi mạng/API, tự dừng bot nếu lỗi liên tiếp.
    """
    global error_count
    try:
        base_capital = get_base_capital()
        capital_to_use = adjust_capital(symbol, strategy, base_capital)

        if builtins.bot_active:
            # 🔥 Thực hiện lệnh (giả lập hoặc thực tế)
            print(f"💰 Đặt lệnh {symbol} với {capital_to_use:.2f} USDT theo chiến lược {strategy}")
            
            # 📝 TÍNH KẾT QUẢ GIẢ LẬP (pnl)
            import random
            pnl = round(random.uniform(-10, 10), 2)  # Tạo PnL giả định
            result = 1 if pnl > 0 else 0
            update_winrate(symbol, strategy, result)  # Cập nhật học tập
            builtins.last_order = f"{symbol} | {strategy} | vốn: {capital_to_use:.2f} USDT | PnL: {pnl}"

            error_count = 0  # Reset lỗi nếu lệnh thành công
        else:
            print(f"⏸ Bot đang dừng, bỏ qua giao dịch {symbol}")

    except Exception as e:
        error_count += 1
        print(f"❌ Lỗi execute_trade {symbol}: {e}")

        if error_count >= MAX_ERRORS:
            builtins.bot_active = False
            print("🚨 Bot tự động dừng do lỗi liên tiếp!")
