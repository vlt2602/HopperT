import time
import builtins
import pandas as pd
from binance_handler import binance, get_best_symbols, monitor_price_and_sell
from strategy_logger import log_to_sheet
from logger_helper import send_telegram
from ai_strategy import select_strategy, select_timeframe, classify_market_state
from risk_manager import check_daily_loss
from strategy_metrics import get_strategy_scores, get_optimal_usdt_amount

def smart_trade_loop():
    while True:
        if hasattr(builtins, "bot_active") and not builtins.bot_active:
            print("⏸ Bot đang tạm dừng (toggle OFF). Đợi 30 giây...")
            time.sleep(30)
            continue

        print("🤖 Bắt đầu vòng lặp giao dịch thông minh...")
        send_telegram("🤖 Đã bắt đầu vòng lặp giao dịch thông minh...")

        symbols = get_best_symbols()
        print("📈 Top coin hiện tại:", symbols)
        send_telegram(f"📈 Đang xét các coin: {', '.join(symbols)}")

        for symbol in symbols:
            print(f"🔁 Bắt đầu xử lý symbol: {symbol}")
            send_telegram(f"🔁 Bắt đầu xử lý symbol: {symbol}")
            try:
                timeframe = select_timeframe(symbol)
                print(f"📥 Fetch dữ liệu nến {symbol} | TF: {timeframe}")
                send_telegram(f"📥 Đang lấy dữ liệu nến {symbol} – {timeframe}")
                ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)

                print(f"✅ Đã fetch xong dữ liệu {symbol}")
                send_telegram(f"✅ Lấy xong dữ liệu nến {symbol}")
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

                selected_strategy = select_strategy(df)
                scores_3d = get_strategy_scores(days=3)
                score_info = scores_3d.get(selected_strategy, {})

                if score_info.get("winrate", 100) < 40:
                    print(f"⚠️ Bỏ qua {symbol} do chiến lược `{selected_strategy}` có winrate thấp ({score_info.get('winrate', 0)}%)")
                    send_telegram(f"🚫 Bỏ qua {symbol} – Winrate {selected_strategy} < 40% (cooldown)")
                    continue

                send_telegram(f"🤖 {symbol} | Timeframe: {timeframe} | Chiến lược: {selected_strategy}")

                balance = binance.fetch_balance()['USDT']['free']
                price = binance.fetch_ticker(symbol)['last']
                amount_usdt = min(get_optimal_usdt_amount(selected_strategy), balance)

                if amount_usdt < 10:
                    print(f"⚠️ {symbol} không đủ vốn để khớp lệnh.")
                    continue

                qty = round(amount_usdt / price, 5)
                binance.create_market_buy_order(symbol, qty)
                send_telegram(f"✅ Đã mua {symbol} {qty} với {amount_usdt:.2f} USDT tại {price:.2f}")
                log_to_sheet(symbol, "BUY", qty, price, selected_strategy, "pending", 0)

                try:
                    monitor_price_and_sell(symbol, qty, price, strategy=selected_strategy)
                except Exception as e:
                    send_telegram(f"❌ Lỗi khi theo dõi và bán: {e}")

                check_daily_loss()
                time.sleep(2)

            except Exception as e:
                send_telegram(f"❌ Lỗi xử lý {symbol}: {e}")

        try:
            market_state = classify_market_state(df)
            delay = 30 if market_state == "trend" else 90 if market_state == "sideway" else 120
        except:
            delay = 60

        print(f"⏳ Chờ {delay} giây trước lần giao dịch tiếp theo...")
        time.sleep(delay)
