# strategy_logger.py (nâng cấp)

import csv
from datetime import datetime
from config import USE_GOOGLE_SHEET, SHEET_WEBHOOK
import requests
from logger import log_error, log_info

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
            log_info(f"Đã log Google Sheet: {symbol} | {strategy} | {result} | PnL: {pnl}")
        except Exception as e:
            log_error(f"Lỗi gửi Google Sheet: {e}")

def log_strategy(symbol, strategy, result, pnl, market_state="unknown"):
    try:
        with open("strategy_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, strategy,
                market_state, result,
                round(pnl, 2)
            ])
        log_info(f"Đã ghi strategy_log: {symbol} | {strategy} | {result} | PnL: {pnl}")
    except Exception as e:
        log_error(f"Lỗi ghi strategy_log.csv: {e}")
