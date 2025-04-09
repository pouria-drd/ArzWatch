import os
import sys

# Add the parent directory to the system path (if needed for module imports)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from telegram import Update
from dotenv import load_dotenv
from extractors.alan_chand import GoldAndCoinExtractor
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Enable logging for debugging and monitoring
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# /start command
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"{user.first_name}" if user.first_name else user.username

    await update.message.reply_text(
        f"""
سلام 👋 <b>{username}</b> عزیز!  
به ربات <b>ArzWatch</b> خوش اومدی 🟢

این ربات برای نمایش قیمت‌های لحظه‌ای بازار طراحی شده 🧠

برای مشاهده دستورات موجود، کافیه از دستور زیر استفاده کنی:
👉 <b>/help</b>
""",
        parse_mode="HTML",
    )


# /help command
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
📚 <b>راهنمای دستورات ربات ArzWatch</b>

🔸 <b>/gold</b> - دریافت قیمت لحظه‌ای مثقال و گرم طلای ۱۸ عیار

🔸 <b>/coin</b> - دریافت قیمت انواع سکه (امامی، بهار، نیم، ربع، گرمی)

🔸 <b>/currency</b> - دریافت نرخ لحظه‌ای ارزهای پرکاربرد (دلار، یورو، پوند و ...)

🔸 <b>/crypto</b> - دریافت قیمت لحظه‌ای ارزهای دیجیتال (بیت‌کوین، اتریوم و ...)

🆘 <b>/help</b> - نمایش همین راهنما

💡 همه‌ی اطلاعات از منابع معتبر و به‌روز جمع‌آوری میشه و ربات هر چند دقیقه یکبار آپدیت میشه!
        """,
        parse_mode="HTML",
    )


# /gold command
async def handle_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extractor = GoldAndCoinExtractor()
    data = extractor.fetch_gold_data()
    last_update = data.get("last_update", "N/A")

    # Split time and date
    time_part = last_update.split(" ")[0]  # ساعت
    date_part = " ".join(last_update.split(" ")[2:])  # تاریخ

    # Find items
    gold_items = data.get("golds", [])
    gram_18k = next((item for item in gold_items if "18" in item["title"]), None)
    misqal = next((item for item in gold_items if "Misqal" in item["title"]), None)

    if not gram_18k or not misqal:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات قیمت طلا")
        return

    # Build response message
    response = f"""
<b>📊 قیمت لحظه‌ای طلا</b>

🗓️ <b>{date_part}</b>   ⏰ <b>{time_part}</b>
———————————————
"""

    response += f"""
<b>🔸 مثقال طلا</b>
💰 قیمت: <b>{misqal['price']} تومان</b>
📈 تغییر: <code>{misqal['change']}</code>
🎈 حباب: <code>{misqal['bubble_amount']}</code> ({misqal['bubble_percentage']})
———————————————
"""

    response += f"""
<b>🔸 هر گرم طلای ۱۸ عیار</b>
💰 قیمت: <b>{gram_18k['price']} تومان</b>
📈 تغییر: <code>{gram_18k['change']}</code>
🎈 حباب: <code>{gram_18k['bubble_amount']}</code> ({gram_18k['bubble_percentage']})
———————————————
"""

    await update.message.reply_text(response, parse_mode="HTML")


# /coins command
async def handle_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extractor = GoldAndCoinExtractor()
    data = extractor.fetch_coin_data()
    last_update = data.get("last_update", "N/A")

    # Split time and date
    time_part = last_update.split(" ")[0]
    date_part = " ".join(last_update.split(" ")[2:])

    # ترجمه‌ی نام سکه‌ها
    coin_title_map = {
        "Imami Coin": "سکه امامی",
        "Bahare Azadi Coin": "سکه بهار آزادی",
        "Half Coin": "نیم‌سکه",
        "Quarter Coin": "ربع‌سکه",
        "Gram Coin": "سکه گرمی",
    }

    coin_items = data.get("coins", [])
    if not coin_items:
        await update.message.reply_text("❌ خطا در دریافت اطلاعات قیمت سکه")
        return

    response = f"""
<b>🪙 قیمت لحظه‌ای سکه</b>

🗓️ <b>{date_part}</b>   ⏰ <b>{time_part}</b>
———————————————
"""

    for coin in coin_items:
        fa_title = coin_title_map.get(
            coin["title"], coin["title"]
        )  # fallback if not found
        response += f"""
<b>🔹 {fa_title}</b>
💰 قیمت: <b>{coin['price']} تومان</b>
📈 تغییر: <code>{coin['change']}</code>
🎈 حباب: <code>{coin['bubble_amount']}</code> ({coin['bubble_percentage']})
———————————————
"""

    await update.message.reply_text(response, parse_mode="HTML")


# General error handler
async def error(update: Update, error: Exception):
    await update.message.reply_text("Something went wrong ...")


# Run the Telegram bot
def run_bot():
    print("Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("gold", handle_gold))
    app.add_handler(CommandHandler("coin", handle_coin))

    # Register error handler
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=5)
