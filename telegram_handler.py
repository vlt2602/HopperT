from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd
from strategy_metrics import get_strategy_scores
from balance_helper import get_balance, get_used_capital

# Khởi tạo biến toàn cục
builtins.panic_mode = False
builtins.loss_streak = 0
builtins.capital_limit = 500
builtins.capital_limit_init = 500
builtins.bot_active = True
builtins.last_order = None

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    state = "🟢 ĐANG CHẠY" if builtins.bot_active else "🔴 ĐANG DỪNG"
    await update.message.reply_text(f"✅ HopperT đang hoạt động!\nTrạng thái bot: {state}")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.panic_mode = False
    builtins.loss_streak = 0
    await update.message.reply_text("✅ Đã gỡ Panic Stop. Tiếp tục giao dịch.")

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.bot_active = not builtins.bot_active
    state = "🟢 Bot ĐANG CHẠY" if builtins.bot_active else "🔴 Bot ĐÃ DỪNG"
    await update.message.reply_text(f"⚙️ Trạng thái bot: {state}")

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    try:
        amount = float(context.args[0])
        builtins.capital_limit = amount
        builtins.capital_limit_init = amount
        await update.message.reply_text(f"✅ Cập nhật vốn tối đa: {amount} USDT")
    except:
        await update.message.reply_text("❌ Sai cú pháp. Dùng: /setcapital [số_usdt]")

async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    total_balance = get_balance()
    used_cap = get_used_capital()
    remaining_cap = total_balance - used_cap
    allowed_cap = builtins.capital_limit
    msg = (f"📊 *QUẢN LÝ VỐN*\n\n"
           f"• Tổng số dư: {total_balance:.2f} USDT\n"
           f"• Vốn cho phép dùng: {allowed_cap:.2f} USDT\n"
           f"• Vốn đang dùng: {used_cap:.2f} USDT\n"
           f"• Vốn còn lại: {remaining_cap:.2f} USDT")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    scores = get_strategy_scores(days=7)
    if not scores:
        await update.message.reply_text("⚠️ Chưa có dữ liệu chiến lược.")
        return
    lines = ["📊 Hiệu suất chiến lược 7 ngày:"]
    for name, s in scores.items():
        lines.append(f"• {name}: {s['winrate']}% | {s['pnl']} USDT | score={s['score']}")
    await update.message.reply_text("\n".join(lines))

async def lastorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    msg = builtins.last_order or "⚠️ Chưa có lệnh nào gần đây."
    await update.message.reply_text(f"📦 Lệnh gần nhất:\n{msg}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    await update.message.reply_text("📅 Báo cáo tự động lúc 05:00 hàng ngày & 05:01 Chủ nhật.")

async def addcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.capital_limit += 100
    builtins.capital_limit_init += 100
    await update.message.reply_text(f"➕ Tăng vốn +100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def removecapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.capital_limit = max(0, builtins.capital_limit - 100)
    builtins.capital_limit_init = max(0, builtins.capital_limit_init - 100)
    await update.message.reply_text(f"➖ Giảm vốn -100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def resetcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.capital_limit = 500
    builtins.capital_limit_init = 500
    await update.message.reply_text("🔁 Reset vốn về mặc định: 500 USDT")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    buttons = [["/status", "/toggle", "/resume", "/pause"],
               ["/capital", "/setcapital 500", "/lastorder"],
               ["/addcapital", "/removecapital", "/strategy"],
               ["/report", "/top", "/resetlog"], ["/menu"]]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("📋 Menu điều khiển HopperT:", reply_markup=markup)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    try:
        df = pd.read_csv("strategy_log.csv", header=None, names=["time", "symbol", "strategy", "result", "pnl"])
        df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
        summary = df.groupby("strategy")["pnl"].sum().sort_values(ascending=False)
        if summary.empty:
            await update.message.reply_text("⚠️ Chưa có dữ liệu chiến lược.")
            return
        best = summary.idxmax()
        await update.message.reply_text(f"🏆 Chiến lược tốt nhất: {best} ({summary[best]:.2f} USDT)")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi /top: {e}")

async def resetlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    try:
        open("strategy_log.csv", "w").close()
        await update.message.reply_text("🗑 Đã xoá toàn bộ log chiến lược.")
    except:
        await update.message.reply_text("❌ Không thể xoá file log.")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    builtins.bot_active = False
    await update.message.reply_text("⏸ Bot đã tạm dừng. Gõ /resume để chạy lại.")

# ✅ KHỞI CHẠY BOT TELEGRAM (hợp chuẩn v20)
async def start_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("toggle", toggle))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("capital", capital))
    app.add_handler(CommandHandler("strategy", strategy))
    app.add_handler(CommandHandler("lastorder", lastorder))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("addcapital", addcapital))
    app.add_handler(CommandHandler("removecapital", removecapital))
    app.add_handler(CommandHandler("resetcapital", resetcapital))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("resetlog", resetlog))
    app.add_handler(CommandHandler("pause", pause))

    print("✅ Telegram bot đang chạy...")
    await app.run_polling()
