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
            'ids': 'bitcoin,ethereum,binancecoin,solana,ripple',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        r = requests.get(url, params=params, timeout=10).json()
        btc = r['bitcoin']
        eth = r['ethereum']
        bnb = r['binancecoin']
        sol = r['solana']
        xrp = r['ripple']

        def arrow(c): return "📈" if c > 0 else "📉"

        return (
            f"💰 أسعار العملات الرقمية:\n\n"
            f"{arrow(btc['usd_24h_change'])} BTC: {btc['usd']:,}$ ({btc['usd_24h_change']:.1f}%)\n"
            f"{arrow(eth['usd_24h_change'])} ETH: {eth['usd']:,}$ ({eth['usd_24h_change']:.1f}%)\n"
            f"{arrow(bnb['usd_24h_change'])} BNB: {bnb['usd']:,}$ ({bnb['usd_24h_change']:.1f}%)\n"
            f"{arrow(sol['usd_24h_change'])} SOL: {sol['usd']:,}$ ({sol['usd_24h_change']:.1f}%)\n"
            f"{arrow(xrp['usd_24h_change'])} XRP: {xrp['usd']:,}$ ({xrp['usd_24h_change']:.1f}%)\n"
        )
    except Exception as e:
        return f"تعذر جلب الأسعار: {e}"

def get_gold():
    try:
        url = "https://api.gold-api.com/price/XAU"
        r = requests.get(url, timeout=10).json()
        price = r.get('price', 'غير متوفر')
        return f"🥇 الذهب: {price}$ للأونصة"
    except Exception as e:
        return f"تعذر جلب سعر الذهب: {e}"

def get_currency(base='USD'):
    try:
        r = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{base}",
            timeout=10
        ).json()
        rates = r['rates']

        base_names = {
            'USD': '🇺🇸 الدولار الأمريكي',
            'SAR': '🇸🇦 الريال السعودي',
            'AED': '🇦🇪 الدرهم الإماراتي',
            'EGP': '🇪🇬 الجنيه المصري',
            'EUR': '🇪🇺 اليورو',
            'GBP': '🇬🇧 الجنيه الإسترليني',
        }

        return (
            f"💵 أسعار الصرف مقابل {base_names.get(base, base)}:\n\n"
            f"🌍 العملات العربية:\n"
            f"🇸🇦 ريال سعودي: {rates.get('SAR')}\n"
            f"🇦🇪 درهم إماراتي: {rates.get('AED')}\n"
            f"🇪🇬 جنيه مصري: {rates.get('EGP')}\n"
            f"🇰🇼 دينار كويتي: {rates.get('KWD')}\n"
            f"🇧🇭 دينار بحريني: {rates.get('BHD')}\n"
            f"🇶🇦 ريال قطري: {rates.get('QAR')}\n"
            f"🇴🇲 ريال عماني: {rates.get('OMR')}\n"
            f"🇯🇴 دينار أردني: {rates.get('JOD')}\n"
            f"🇱🇧 ليرة لبنانية: {rates.get('LBP')}\n"
            f"🇮🇶 دينار عراقي: {rates.get('IQD')}\n"
            f"🇩🇿 دينار جزائري: {rates.get('DZD')}\n"
            f"🇲🇦 درهم مغربي: {rates.get('MAD')}\n"
            f"🇹🇳 دينار تونسي: {rates.get('TND')}\n"
            f"🇱🇾 دينار ليبي: {rates.get('LYD')}\n"
            f"🇸🇩 جنيه سوداني: {rates.get('SDG')}\n\n"
            f"🌐 العملات الأجنبية:\n"
            f"🇺🇸 دولار أمريكي: {rates.get('USD')}\n"
            f"🇪🇺 يورو: {rates.get('EUR')}\n"
            f"🇬🇧 جنيه إسترليني: {rates.get('GBP')}\n"
            f"🇨🇭 فرنك سويسري: {rates.get('CHF')}\n"
            f"🇯🇵 ين ياباني: {rates.get('JPY')}\n"
            f"🇨🇳 يوان صيني: {rates.get('CNY')}\n"
            f"🇨🇦 دولار كندي: {rates.get('CAD')}\n"
            f"🇦🇺 دولار أسترالي: {rates.get('AUD')}\n"
            f"🇮🇳 روبية هندية: {rates.get('INR')}\n"
            f"🇹🇷 ليرة تركية: {rates.get('TRY')}\n"
            f"🇷🇺 روبل روسي: {rates.get('RUB')}\n"
            f"🇰🇷 وون كوري: {rates.get('KRW')}\n"
            f"🇧🇷 ريال برازيلي: {rates.get('BRL')}\n"
            f"🇸🇬 دولار سنغافوري: {rates.get('SGD')}\n"
            f"🇳🇴 كرون نرويجي: {rates.get('NOK')}\n"
            f"🇸🇪 كرون سويدي: {rates.get('SEK')}\n"
        )
    except Exception as e:
        return f"تعذر جلب أسعار الصرف: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
        [InlineKeyboardButton("🥇 سعر الذهب", callback_data='gold')],
        [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency_menu')],
        [InlineKeyboardButton("📊 كل الأسعار بالدولار", callback_data='all_USD')]
    ]
    await update.message.reply_text(
        "👋 مرحباً في بوت الخبير الاقتصادي!\n\n"
        "أحصل على آخر الأسعار والمعلومات الاقتصادية\n"
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

    elif query.data == 'currency_menu':
        keyboard = [
            [InlineKeyboardButton("🇺🇸 مقابل الدولار", callback_data='cur_USD')],
            [InlineKeyboardButton("🇸🇦 مقابل الريال السعودي", callback_data='cur_SAR')],
            [InlineKeyboardButton("🇦🇪 مقابل الدرهم الإماراتي", callback_data='cur_AED')],
            [InlineKeyboardButton("🇪🇬 مقابل الجنيه المصري", callback_data='cur_EGP')],
            [InlineKeyboardButton("🇪🇺 مقابل اليورو", callback_data='cur_EUR')],
            [InlineKeyboardButton("🇬🇧 مقابل الجنيه الإسترليني", callback_data='cur_GBP')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
        ]
        await query.message.reply_text(
            "اختر العملة الأساسية للمقارنة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith('cur_'):
        base = query.data.replace('cur_', '')
        await query.message.reply_text("⏳ جاري جلب الأسعار...")
        await query.message.reply_text(get_currency(base))

    elif query.data.startswith('all_'):
        base = query.data.replace('all_', '')
        await query.message.reply_text("⏳ جاري جلب كل الأسعار...")
        msg = f"{get_crypto()}\n\n{get_gold()}\n\n{get_currency(base)}"
        await query.message.reply_text(msg)

    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
            [InlineKeyboardButton("🥇 سعر الذهب", callback_data='gold')],
            [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency_menu')],
            [InlineKeyboardButton("📊 كل الأسعار بالدولار", callback_data='all_USD')]
        ]
        await query.message.reply_text(
            "اختر ما تريد:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()
