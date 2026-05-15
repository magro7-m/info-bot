import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

def get_crypto():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        r = requests.get(url, params=params, timeout=10).json()
        btc = r['bitcoin']
        eth = r['ethereum']
        return (
            f"₿ BTC: {btc['usd']:,}$"
            f" ({btc['usd_24h_change']:.1f}%)\n"
            f"Ξ ETH: {eth['usd']:,}$"
            f" ({eth['usd_24h_change']:.1f}%)"
        )
    except Exception as e:
        return f"تعذر جلب الأسعار: {e}"

def get_gold():
    try:
        r = requests.get(
            "https://api.metals.live/v1/spot/gold",
            timeout=10
        ).json()
        return f"🥇 الذهب: {r[0]['price']}$ للأونصة"
    except Exception as e:
        return f"تعذر جلب سعر الذهب: {e}"

def get_currency():
    try:
        r = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        ).json()
        rates = r['rates']
        return (
            f"💵 أسعار الصرف:\n"
            f"ريال سعودي: {rates.get('SAR')}\n"
            f"درهم: {rates.get('AED')}\n"
            f"جنيه مصري: {rates.get('EGP')}\n"
            f"يورو: {rates.get('EUR')}"
        )
    except Exception as e:
        return f"تعذر جلب أسعار الصرف: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
        [InlineKeyboardButton("🥇 سعر الذهب", callback_data='gold')],
        [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency')],
        [InlineKeyboardButton("📊 كل الأسعار", callback_data='all')]
    ]
    await update.message.reply_text(
        "👋 مرحباً في بوت الخبير الاقتصادي!\n"
        "اختر ما تريد:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'crypto':
        await query.message.reply_text(get_crypto())
    elif query.data == 'gold':
        await query.message.reply_text(get_gold())
    elif query.data == 'currency':
        await query.message.reply_text(get_currency())
    elif query.data == 'all':
        msg = f"{get_crypto()}\n\n{get_gold()}\n\n{get_currency()}"
        await query.message.reply_text(msg)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()
