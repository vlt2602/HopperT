<<<<<<< HEAD
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd
from datetime import datetime, timedelta
from balance_helper import get_balance, get_used_capital
from binance_handler import binance

# Biến toàn cục
=======
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd

>>>>>>> 5a8f10b (Update telegram_handler.py với menu inline mới)
builtins.panic_mode = False
builtins.loss_streak = 0
builtins.capital_limit = 500
builtins.capital_limit_init = 500
builtins.bot_active = True
builtins.last_order = None

<<<<<<< HEAD
bot = Bot(token=TELEGRAM_TOKEN)

def send_alert(message):
    try:
        bot.send_message(chat_id=ALLOWED_CHAT_ID, text=message)
    except Exception as e:
        print(f"❌ Lỗi gửi tin Telegram: {e}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    buttons = [
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("⚙️ Toggle", callback_data="toggle")],
        [InlineKeyboardButton("💰 Capital", callback_data="capital"),
         InlineKeyboardButton("💵 Vốn 500$", callback_data="resetcapital")],
        [InlineKeyboardButton("➕ Tăng +100$", callback_data="addcapital"),
         InlineKeyboardButton("➖ Giảm -100$", callback_data="removecapital")],
        [InlineKeyboardButton("🗑 Reset Log", callback_data="resetlog"),
         InlineKeyboardButton("📋 Check Logs", callback_data="checklogs")],
        [InlineKeyboardButton("▶️ Resume", callback_data="resume"),
         InlineKeyboardButton("💲 Setcapital", callback_data="setcapital")],
        [InlineKeyboardButton("📈 Lệnh hôm nay", callback_data="todayorders"),
         InlineKeyboardButton("📊 Báo cáo 24h", callback_data="report24h"),
         InlineKeyboardButton("📊 Báo cáo tổng", callback_data="reportall")]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("📋 Menu điều khiển HopperT:", reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    handlers = {
        "status": status, "toggle": toggle, "capital": capital, "resetcapital": resetcapital,
        "addcapital": addcapital, "removecapital": removecapital, "resetlog": resetlog,
        "checklogs": checklogs, "resume": resume, "setcapital": setcapital,
        "todayorders": todayorders, "report24h": report24h, "reportall": reportall
    }
    if data in handlers: await handlers[data](update, context)

async def status(update, context): await update.effective_chat.send_message("🟢 HopperT đang chạy" if builtins.bot_active else "🔴 HopperT đã dừng")
async def toggle(update, context): builtins.bot_active = not builtins.bot_active; await update.effective_chat.send_message("🟢 Bot ĐANG CHẠY" if builtins.bot_active else "🔴 Bot ĐÃ DỪNG")
async def capital(update, context):
    balances = binance.fetch_balance()
    total_usdt, details = 0, []
    for coin, info in balances.items():
        if (free := info['free']) > 0:
            if coin == 'USDT': total_usdt += free; details.append(f"{coin}: {free:.2f} USDT")
            else:
                try: price = binance.fetch_ticker(f"{coin}/USDT")['last']; equiv = free * price
                except: price, equiv = 0, 0
                total_usdt += equiv; details.append(f"{coin}: {free} (~{equiv:.2f} USDT)")
    used, allowed = get_used_capital(), builtins.capital_limit
    await update.effective_chat.send_message(f"💰 Tổng: ~{total_usdt:.2f} USDT\n" + "\n".join(details) + f"\nVốn cho phép: {allowed} USDT\nĐã dùng: {used} USDT\nCòn lại: {allowed - used} USDT")
async def resetcapital(update, context): builtins.capital_limit = builtins.capital_limit_init = 500; await update.effective_chat.send_message("🔁 Vốn mặc định 500 USDT")
async def addcapital(update, context): builtins.capital_limit += 100; builtins.capital_limit_init += 100; await update.effective_chat.send_message(f"➕ Tăng +100, hiện tại: {builtins.capital_limit} USDT")
async def removecapital(update, context): builtins.capital_limit = max(0, builtins.capital_limit-100); builtins.capital_limit_init = max(0, builtins.capital_limit_init-100); await update.effective_chat.send_message(f"➖ Giảm -100, hiện tại: {builtins.capital_limit} USDT")
async def resetlog(update, context): open("strategy_log.csv", "w").close(); await update.effective_chat.send_message("🗑 Đã reset log")
async def checklogs(update, context): await update.effective_chat.send_message("📋 Đang kiểm tra log hệ thống (chưa triển khai)")
async def resume(update, context): builtins.panic_mode = False; builtins.loss_streak = 0; await update.effective_chat.send_message("▶️ Đã resume")
async def setcapital(update, context): await update.effective_chat.send_message("❓ Dùng /setcapital [số] để đặt vốn")
async def todayorders(update, context): await update.effective_chat.send_message("📋 Danh sách lệnh hôm nay (chưa triển khai)")
async def report24h(update, context): await update.effective_chat.send_message("📊 Báo cáo 24h (chưa triển khai)")
async def reportall(update, context): await update.effective_chat.send_message("📊 Báo cáo tổng (chưa triển khai)")

async def start_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot Telegram chạy...")
=======
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
    await update.message.reply_text(f"💰 Vốn giới hạn: {builtins.capital_limit} USDT")

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

async def lastorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    msg = builtins.last_order or "⚠️ Chưa có lệnh nào gần đây."
    await update.message.reply_text(f"📦 Lệnh gần nhất:\n{msg}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    await update.message.reply_text("📅 Báo cáo tự động lúc 05:00 hàng ngày & 05:01 Chủ nhật.")

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

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    buttons = [["/status", "/toggle", "/resume", "/pause"],
               ["/capital", "/setcapital 500", "/lastorder"],
               ["/addcapital", "/removecapital", "/report"],
               ["/top", "/resetlog", "/menu"]]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("📋 Menu điều khiển HopperT:", reply_markup=markup)

async def start_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("toggle", toggle))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("capital", capital))
    app.add_handler(CommandHandler("lastorder", lastorder))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("addcapital", addcapital))
    app.add_handler(CommandHandler("removecapital", removecapital))
    app.add_handler(CommandHandler("resetcapital", resetcapital))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("resetlog", resetlog))
    app.add_handler(CommandHandler("pause", pause))
    print("✅ Telegram bot đã sẵn sàng...")
>>>>>>> 5a8f10b (Update telegram_handler.py với menu inline mới)
    await app.run_polling()
