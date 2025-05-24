from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd
from datetime import datetime, timedelta
from balance_helper import get_balance, get_used_capital
from binance_handler import binance

# Biến toàn cục
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
    await app.run_polling()
