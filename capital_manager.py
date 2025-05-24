# capital_manager.py

from strategy_manager import check_winrate
import builtins
from logger import log_info, log_error

def adjust_capital(symbol, strategy, base_capital):
    """
    Tự động điều chỉnh vốn dựa trên winrate của chiến lược và cặp coin.
    Nếu winrate > 70%: tăng vốn 1.5 lần.
    Nếu winrate < 30%: giảm vốn còn 0.5 lần.
    """
    try:
        winrate = check_winrate(symbol, strategy)
        if winrate > 70:
            log_info(f"🚀 Winrate cao {winrate}%, tăng vốn.")
            return base_capital * 1.5  # Tăng vốn 1.5 lần
        elif winrate < 30:
            log_info(f"⚠️ Winrate thấp {winrate}%, giảm vốn.")
            return base_capital * 0.5  # Giảm vốn còn 0.5 lần
        else:
            log_info(f"🔍 Winrate ổn định {winrate}%, giữ vốn gốc.")
            return base_capital
    except Exception as e:
        log_error(f"❌ Lỗi tính vốn {symbol}: {e}")
        return base_capital

def get_base_capital():
    """
    Lấy vốn gốc hiện tại từ builtins.
    """
    return builtins.capital_limit
