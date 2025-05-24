from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd
from strategy_metrics import get_strategy_scores
from balance_helper import get_balance, get_used_capital
from binance_handler import binance

# Khởi tạo biến toàn cục
builtins.panic_mode = False
builtins.loss_streak = 0
builtins.capital_limit = 500
builtins.capital_limit_init = 500
builtins.bot_active = True
builtins.last_order = None

bot = Bot(token=TELEGRAM_TOKEN)

def send_alert(message):
    try:
        bot.send_message(chat_id=ALLOWED_CHAT_ID, text=message)
    except Exception as e:
        print(f"❌ Lỗi gửi tin Telegram: {e}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
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
    if data == "status": await status(update, context)
    elif data == "toggle": await toggle(update, context)
    elif data == "capital": await capital(update, context)
    elif data == "resetcapital": await resetcapital(update, context)
    elif data == "addcapital": await addcapital(update, context)
    elif data == "removecapital": await removecapital(update, context)
    elif data == "resetlog": await resetlog(update, context)
    elif data == "checklogs": await checklogs(update, context)
    elif data == "resume": await resume(update, context)
    elif data == "setcapital": await setcapital(update, context)
    elif data == "todayorders": await todayorders(update, context)
    elif data == "report24h": await report24h(update, context)
    elif data == "reportall": await reportall(update, context)

async def status(update, context): await update.effective_chat.send_message("🟢 HopperT đang chạy" if builtins.bot_active else "🔴 HopperT đã dừng")

async def toggle(update, context):
    builtins.bot_active = not builtins.bot_active
    await update.effective_chat.send_message("🟢 Bot ĐANG CHẠY" if builtins.bot_active else "🔴 Bot ĐÃ DỪNG")

async def capital(update, context):
    balances = binance.fetch_balance()
    total_usdt = 0
    details = []
    for coin, info in balances.items():
        free = info['free']
        if free > 0:
            if coin == 'USDT':
                total_usdt += free
                details.append(f"{coin}: {free:.2f} USDT")
            else:
                try:
                    price = binance.fetch_ticker(f"{coin}/USDT")['last']
                    equiv = free * price
                    total_usdt += equiv
                    details.append(f"{coin}: {free} (~{equiv:.2f} USDT)")
                except:
                    details.append(f"{coin}: {free} (không có giá)")
    used_cap = get_used_capital()
    allowed = builtins.capital_limit
    await update.effective_chat.send_message(f"💰 Tổng số dư ~{total_usdt:.2f} USDT\n" + "\n".join(details) + f"\nVốn cho phép: {allowed} USDT\nVốn đã dùng: {used_cap} USDT\nVốn còn lại: {allowed - used_cap} USDT")

async def resetcapital(update, context):
    builtins.capital_limit = 500
    builtins.capital_limit_init = 500
    await update.effective_chat.send_message("🔁 Vốn mặc định 500 USDT đã được đặt lại.")

async def addcapital(update, context):
    builtins.capital_limit += 100
    builtins.capital_limit_init += 100
    await update.effective_chat.send_message(f"➕ Tăng vốn +100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def removecapital(update, context):
    builtins.capital_limit = max(0, builtins.capital_limit - 100)
    builtins.capital_limit_init = max(0, builtins.capital_limit_init - 100)
    await update.effective_chat.send_message(f"➖ Giảm vốn -100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def resetlog(update, context):
    open("strategy_log.csv", "w").close()
    await update.effective_chat.send_message("🗑 Đã reset log chiến lược.")

async def checklogs(update, context):
    await update.effective_chat.send_message("📋 Đang kiểm tra log hệ thống...")
    # TODO: Đọc file log deploy hoặc API logs và gửi về Telegram

async def resume(update, context):
    builtins.panic_mode = False
    builtins.loss_streak = 0
    await update.effective_chat.send_message("▶️ Bot đã tiếp tục giao dịch.")

async def setcapital(update, context):
    await update.effective_chat.send_message("❓ Dùng lệnh /setcapital [số] để đặt vốn tùy chỉnh.")

async def todayorders(update, context):
    # TODO: Lọc file log hoặc database để lấy danh sách lệnh hôm nay
    await update.effective_chat.send_message("📋 Danh sách lệnh hôm nay:\n(Chưa triển khai)")

async def report24h(update, context):
    await update.effective_chat.send_message("📊 Báo cáo 24h:\n(Chưa triển khai)")

async def reportall(update, context):
    await update.effective_chat.send_message("📊 Báo cáo tổng thời gian:\n(Chưa triển khai)")

async def start_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Telegram bot đang chạy...")
    await app.run_polling()
