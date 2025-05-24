# report_scheduler.py

import schedule
import time
import pandas as pd
from datetime import datetime, timedelta
from logger import log_info, log_error
from report_helper import log_daily_report, send_uptime_report
from logger_helper import send_telegram

LOG_FILE = "strategy_log.csv"

def read_log():
    try:
        df = pd.read_csv(LOG_FILE,
                         header=None,
                         names=["time", "symbol", "strategy", "result", "pnl"])
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        log_error(f"[Báo cáo] Không thể đọc file log: {e}")
        return pd.DataFrame()

def summarize(df, start, end):
    df_range = df[(df["time"] >= start) & (df["time"] < end)]
    if df_range.empty:
        return "⚠️ Không có dữ liệu giao dịch trong giai đoạn này."

    summary = df_range.groupby("strategy").agg(orders=("result", "count"),
                                               wins=("result", lambda x:
                                                     (x == "win").sum()),
                                               losses=("result", lambda x:
                                                       (x == "loss").sum()),
                                               pnl=("pnl",
                                                    "sum")).reset_index()

    result_lines = []
    best = summary.sort_values(by="pnl", ascending=False).iloc[0]

    for _, row in summary.iterrows():
        winrate = (row["wins"] / row["orders"]) * 100
        result_lines.append(
            f"📌 {row['strategy']}: {row['orders']} lệnh | Winrate: {winrate:.0f}% | PnL: {row['pnl']:.2f} USDT"
        )

    message = "\n".join([
        f"📊 Báo cáo hiệu suất ({start.strftime('%d/%m')} - {end.strftime('%d/%m')}):",
        *result_lines,
        f"\n🏆 Chiến lược tốt nhất: {best['strategy']} ({best['pnl']:.2f} USDT)"
    ])
    return message

def daily_report():
    now = datetime.now()
    df = read_log()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    df_today = df[(df["time"] >= start) & (df["time"] < end)]

    if df_today.empty:
        send_telegram("📅 *Báo cáo ngày*: Hôm nay chưa có giao dịch nào.")
        return

    total_orders = len(df_today)
    total_pnl = df_today["pnl"].sum()
    top_strategy = (df_today.groupby("strategy")["pnl"].sum().sort_values(
        ascending=False).index[0])

    wins = (df_today["result"] == "win").sum()
    winrate = (wins / total_orders) * 100

    msg = (f"📊 *BÁO CÁO GIAO DỊCH HÔM NAY*\n\n"
           f"• Số lệnh: {total_orders}\n"
           f"• Lệnh thắng: {wins} ({winrate:.1f}%)\n"
           f"• Chiến lược hiệu quả nhất: `{top_strategy}`\n"
           f"• Lợi nhuận (PnL): {total_pnl:.2f} USDT\n\n"
           f"⏰ Thời gian: {now.strftime('%d/%m/%Y')}")
    send_telegram(msg)

    try:
        log_daily_report()
    except Exception as e:
        log_error(f"[Lỗi gửi Google Sheets]: {e}")

def weekly_report():
    now = datetime.now()
    df = read_log()
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=7)
    msg = summarize(df, start, end)
    send_telegram("🗓️ Báo cáo tuần:\n" + msg)

def run_scheduler():
    schedule.every().day.at("05:00").do(daily_report)
    schedule.every().day.at("06:00").do(send_uptime_report)
    schedule.every().sunday.at("05:01").do(weekly_report)
    schedule.every().sunday.at("05:02").do(send_weekly_top_strategy)

    while True:
        schedule.run_pending()
        time.sleep(10)

def send_weekly_top_strategy():
    try:
        df = pd.read_csv("strategy_log.csv",
                         header=None,
                         names=[
                             "time", "symbol", "strategy", "market_state",
                             "result", "pnl"
                         ])
        df["time"] = pd.to_datetime(df["time"])
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
        df = df.dropna(subset=["pnl"])

        now = datetime.now()
        start = now - timedelta(days=7)
        df = df[df["time"] >= start]

        if df.empty:
            send_telegram("📉 Không có dữ liệu giao dịch trong 7 ngày qua.")
            return

        summary = df.groupby("strategy").agg(
            total_pnl=("pnl", "sum"),
            orders=("result", "count"),
            wins=("result", lambda x: (x == "win").sum())).reset_index()

        summary["winrate"] = (summary["wins"] / summary["orders"]) * 100
        top = summary.sort_values(by="total_pnl", ascending=False).iloc[0]

        message = ("🏆 *CHIẾN LƯỢC TỐT NHẤT TUẦN*\n\n"
                   f"• Tên chiến lược: `{top['strategy']}`\n"
                   f"• Lệnh thực hiện: {top['orders']} lệnh\n"
                   f"• Winrate: {top['winrate']:.1f}%\n"
                   f"• PnL: {top['total_pnl']:.2f} USDT")
        send_telegram(message)

        with open("top_strategy.csv", mode="a", newline="") as file:
            file.write(
                f"{datetime.now().strftime('%Y-%m-%d')},{top['strategy']},{top['orders']},{top['winrate']:.1f},{top['total_pnl']:.2f}\n"
            )
    except Exception as e:
        log_error(f"❌ Lỗi gửi báo cáo chiến lược tuần: {e}")
