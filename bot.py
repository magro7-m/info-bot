import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

def get_crypto():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd', 'include_24hr_change': 'true'}
        r = requests.get(url, params=params, timeout=10).json()
        btc = r['bitcoin']
        eth = r['ethereum']
        return f"₿ BTC: {btc['usd']:,}$ ({btc['usd_24h_change']:.1f}%)\nΞ ETH: {eth['usd']:,}$ ({eth['usd_24h_change']:.1f}%)"
    except:
        return "تعذر جلب الأسعار حالياً"

def get_gold():
    try:
        r = requests.get("https://api.metals.live/v1/spot/gold", timeout=10).json()
        return f"🥇 الذهب: {r[0]['price']}$ للأونصة"
    except:
        return "تعذر جلب سعر الذهب"

def get_currency():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        rates = r['rates']
        return f"💵 أسعار الصرف:\nريال سعودي: {rates.get('SAR')}\nدرهم: {rates.get('AED')}\nجنيه مصري: {rates.get('EGP')}\nيورو: {rates.get('EUR')}"
    except:
        return "تعذر جلب أسعار الصرف"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
        [InlineKeyboardButton("🥇 سعر الذهب", callback_data='gold')],
        [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency')],
        [InlineKeyboardButton("📊 كل الأسعار", callback_data='all')]
    ]
    await update.message.reply_text(
        "👋 مرحباً في بوت الخبير الاقتصادي!\nاختر ما تريد:",
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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    log.info("البوت يعمل!")
    app.run_polling()

if __name__ == "__main__":
    main()
