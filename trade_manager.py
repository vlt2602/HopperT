# trade_manager.py

from capital_manager import adjust_capital, get_base_capital
import builtins

async def execute_trade(symbol, strategy):
    """
    Hàm xử lý giao dịch thực tế.
    Tích hợp điều chỉnh vốn tự động theo winrate.
    """
    try:
        # Lấy vốn gốc và điều chỉnh vốn dựa trên winrate
        base_capital = get_base_capital()
        capital_to_use = adjust_capital(symbol, strategy, base_capital)

        # 🔥 Thực hiện giao dịch (giả lập hoặc gọi API Binance thực tế)
        if builtins.bot_active:
            print(f"💰 Đặt lệnh {symbol} với {capital_to_use:.2f} USDT theo chiến lược {strategy}")
            # TODO: Tích hợp gọi API Binance nếu muốn thực tế
            # Ví dụ: binance_client.order_market_buy(symbol=symbol, quantity=calculated_quantity)
            builtins.last_order = f"{symbol} | {strategy} | vốn: {capital_to_use:.2f} USDT"
        else:
            print(f"⏸ Bot đang dừng, bỏ qua giao dịch {symbol}")
    except Exception as e:
        print(f"❌ Lỗi execute_trade {symbol}: {e}")
