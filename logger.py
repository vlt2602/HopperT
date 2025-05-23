# logger.py

import requests
import csv
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SHEET_WEBHOOK, USE_GOOGLE_SHEET

# ✅ Ghi lệnh mua/bán lên Google Sheet (nếu bật USE_GOOGLE_SHEET)
def log_to_sheet(symbol, side, qty, price, strategy, result, pnl):
    if USE_GOOGLE_SHEET and SHEET_WEBHOOK:
        try:
            payload = {
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Symbol": symbol,
                "Side": side,
                "Qty": qty,
                "Price": price,
                "Strategy": strategy,
                "Result": result,
                "PnL": pnl
            }
            requests.post(SHEET_WEBHOOK, json=payload)
        except Exception as e:
            print("❌ Lỗi gửi dữ liệu lên Google Sheets:", e)

# ✅ Ghi log chiến lược vào file CSV để thống kê hiệu suất
def log_strategy(symbol, strategy, result, pnl, market_state=""):
    try:
        with open("strategy_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                strategy,
                market_state,
                result,
                round(pnl, 2)
            ])
    except Exception as e:
        print("❌ Lỗi ghi strategy_log.csv:", e)
