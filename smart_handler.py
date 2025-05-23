# smart_handler.py

import time
import builtins
import pandas as pd
from binance_handler import binance, get_best_symbols, monitor_price_and_sell
from strategy_logger import log_to_sheet, log_strategy
from logger_helper import send_telegram
from ai_strategy import select_strategy, select_timeframe


def smart_trade_loop():
    while True:
        if hasattr(builtins, "bot_active") and not builtins.bot_active:
            print("⏸ Bot đang tạm dừng (toggle OFF). Đợi 30 giây...")
            time.sleep(30)
            continue

        print("🤖 Bắt đầu vòng lặp giao dịch thông minh...")
        send_telegram("🤖 Đã bắt đầu vòng lặp giao dịch thông minh...")

        for symbol in get_best_symbols():
            print(f"🔁 Bắt đầu xử lý symbol: {symbol}")
            send_telegram(f"🔁 Bắt đầu xử lý symbol: {symbol}")
            try:
                # ====== CHỌN TIMEFRAME THEO BIẾN ĐỘNG ======
                timeframe = select_timeframe(symbol)

                # ====== LẤY DỮ LIỆU NẾN THEO TIMEFRAME ======
                print(f"📥 Fetch dữ liệu nến {symbol} | TF: {timeframe}")
                send_telegram(f"📥 Đang lấy dữ liệu nến {symbol} – {timeframe}")

                ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)

                print(f"✅ Đã fetch xong dữ liệu {symbol}")
                send_telegram(f"✅ Lấy xong dữ liệu nến {symbol}")
                # ✅ Tạm bỏ qua fetch ohlcv để ép chạy tiếp
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

                # ====== AI CHỌN CHIẾN LƯỢC DỰA TRÊN DỮ LIỆU ======
                selected_strategy = select_strategy(df)
                from strategy_metrics import get_strategy_scores

                scores_3d = get_strategy_scores(days=3)
                score_info = scores_3d.get(selected_strategy, {})

                if score_info.get("winrate", 100) < 40:
                    print(f"⚠️ Bỏ qua {symbol} do chiến lược `{selected_strategy}` có winrate thấp ({score_info.get('winrate', 0)}%)")
                    send_telegram(f"🚫 Bỏ qua {symbol} – Winrate {selected_strategy} < 40% (cooldown)")
                    continue

                send_telegram(
                    f"🤖 {symbol} | Timeframe: {timeframe} | Chiến lược: {selected_strategy}"
                )

                # ====== TÍNH VỐN VÀ VÀO LỆNH ======
                balance = binance.fetch_balance()['USDT']['free']
                price = binance.fetch_ticker(symbol)['last']
                from strategy_metrics import get_optimal_usdt_amount
                amount_usdt = min(get_optimal_usdt_amount(selected_strategy),
                                  balance)
                if amount_usdt < 10:
                    print(f"⚠️ {symbol} không đủ vốn để khớp lệnh.")
                    continue

                qty = round(amount_usdt / price, 5)
                binance.create_market_buy_order(symbol, qty)

                send_telegram(
                    f"✅ Đã mua {symbol} {qty} với {amount_usdt:.2f} USDT tại {price:.2f}"
                )
                log_to_sheet(symbol, "BUY", qty, price, selected_strategy,
                             "pending", 0)

                # ====== THEO DÕI VÀ BÁN THEO CHIẾN LƯỢC ======
                monitor_price_and_sell(symbol,
                                       qty,
                                       price,
                                       strategy=selected_strategy)
                from risk_manager import check_daily_loss
check_daily_loss()

                time.sleep(2)

            except Exception as e:
                send_telegram(f"❌ Lỗi xử lý {symbol}: {e}")

        # === Điều chỉnh tần suất giao dịch theo thị trường ===
        try:
            market_state = classify_market_state(df)
            if market_state == "trend":
                delay = 30
            elif market_state == "sideway":
                delay = 90
            else:
                delay = 120
        except:
            delay = 60

        print(f"⏳ Chờ {delay} giây trước lần giao dịch tiếp theo...")
        time.sleep(delay)

