# logger.py

import requests
import csv
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, USE_GOOGLE_SHEET

# ✅ Đặt webhook URL mới (link Google Apps Script đã tạo)
SHEET_WEBHOOK = "https://script.google.com/macros/s/AKfycbxi3W8SK9HMOJicjTvka9HCxvPC17HPWKpwFGa6MDT9KCqZsRyUMDoq1M_oa9GZV_LTSQ/exec"

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
            response = requests.post(SHEET_WEBHOOK, json=payload)
            if response.status_code == 200:
                print(f"📈 Đã gửi log lên Google Sheet: {symbol}, {strategy}, {result}, {pnl}")
            else:
                print(f"❌ Lỗi gửi log: {response.text}")
        except Exception as e:
            print(f"❌ Lỗi gửi dữ liệu lên Google Sheets: {e}")

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
        print(f"❌ Lỗi ghi strategy_log.csv: {e}")
