import asyncio
import builtins
import pandas as pd
from binance_handler import binance, get_best_symbols
from price_watcher import monitor_price_and_sell
from logger_helper import log_info, log_error
from strategy_logger import log_to_sheet
from ai_strategy import select_timeframe
from market_classifier import classify_market_state
from risk_manager import check_daily_loss
from strategy_metrics import get_strategy_scores, get_optimal_usdt_amount
from strategy_manager import get_best_strategy

async def smart_trade_loop():
    while builtins.bot_active:
        log_info("🤖 Bắt đầu vòng lặp giao dịch thông minh...")

        symbols = get_best_symbols()
        log_info(f"📈 Đang xét các coin: {', '.join(symbols)}")

        current_strategy = get_best_strategy()
        log_info(f"🔥 Sử dụng chiến lược tốt nhất: {current_strategy}")

        for symbol in symbols:
            log_info(f"🔁 Bắt đầu xử lý symbol: {symbol}")
            try:
                timeframe = select_timeframe(symbol)
                log_info(f"📥 Đang lấy dữ liệu nến {symbol} – {timeframe}")
                ohlcv = await asyncio.to_thread(binance.fetch_ohlcv, symbol, timeframe, 50)

                log_info(f"✅ Lấy xong dữ liệu nến {symbol}")
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

                scores_3d = get_strategy_scores(days=3)
                score_info = scores_3d.get(current_strategy, {})

                if score_info.get("winrate", 100) < 40:
                    log_info(f"🚫 Bỏ qua {symbol} – Winrate {current_strategy} < 40% (cooldown)")
                    continue

                log_info(f"🤖 {symbol} | Timeframe: {timeframe} | Chiến lược: {current_strategy}")

                balance = (await asyncio.to_thread(binance.fetch_balance))['USDT']['free']
                price = (await asyncio.to_thread(binance.fetch_ticker, symbol))['last']
                amount_usdt = min(get_optimal_usdt_amount(current_strategy), balance)

                if amount_usdt < 10:
                    log_info(f"⚠️ {symbol} không đủ vốn để khớp lệnh.")
                    continue

                qty = round(amount_usdt / price, 5)
                await asyncio.to_thread(binance.create_market_buy_order, symbol, qty)
                log_to_sheet(symbol, "BUY", qty, price, current_strategy, "pending", 0)

                try:
                    await asyncio.to_thread(monitor_price_and_sell, symbol, qty, price, current_strategy)
                except Exception as e:
                    log_error(f"❌ Lỗi khi theo dõi và bán: {e}")

                check_daily_loss()
                await asyncio.sleep(2)

            except Exception as e:
                log_error(f"❌ Lỗi xử lý {symbol}: {e}")

        try:
            market_state = classify_market_state(df)
            delay = 30 if market_state == "trend" else 90 if market_state == "sideway" else 120
        except Exception as e:
            log_error(f"Lỗi xác định thị trường: {e}")
            delay = 60

        log_info(f"⏳ Chờ {delay} giây trước lần giao dịch tiếp theo...")
        await asyncio.sleep(delay)
