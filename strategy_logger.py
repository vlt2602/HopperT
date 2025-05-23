# strategy_logger.py (nâng cấp)

import csv
from datetime import datetime
from config import USE_GOOGLE_SHEET, SHEET_WEBHOOK
import requests


def log_to_sheet(symbol,
                 side,
                 qty,
                 price,
                 strategy,
                 result,
                 pnl,
                 market_state="unknown"):
    if USE_GOOGLE_SHEET and SHEET_WEBHOOK:
        try:
            payload = {
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Symbol": symbol,
                "Side": side,
                "Qty": qty,
                "Price": price,
                "Strategy": strategy,
                "MarketState": market_state,
                "Result": result,
                "PnL": pnl
            }
            requests.post(SHEET_WEBHOOK, json=payload)
        except Exception as e:
            print("Lỗi gửi Google Sheet:", e)


def log_strategy(symbol, strategy, result, pnl, market_state="unknown"):
    try:
        with open("strategy_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, strategy,
                market_state, result,
                round(pnl, 2)
            ])
    except Exception as e:
        print("Lỗi ghi strategy_log.csv:", e)
