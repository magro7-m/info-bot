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
            'ids': 'bitcoin,ethereum,binancecoin,solana,ripple,cardano,dogecoin,polkadot,litecoin,chainlink',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        r = requests.get(url, params=params, timeout=10).json()
        def arrow(c): return "📈" if c > 0 else "📉"
        return (
            f"💰 أسعار العملات الرقمية:\n\n"
            f"{arrow(r['bitcoin']['usd_24h_change'])} BTC: {r['bitcoin']['usd']:,}$ ({r['bitcoin']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['ethereum']['usd_24h_change'])} ETH: {r['ethereum']['usd']:,}$ ({r['ethereum']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['binancecoin']['usd_24h_change'])} BNB: {r['binancecoin']['usd']:,}$ ({r['binancecoin']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['solana']['usd_24h_change'])} SOL: {r['solana']['usd']:,}$ ({r['solana']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['ripple']['usd_24h_change'])} XRP: {r['ripple']['usd']:,}$ ({r['ripple']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['cardano']['usd_24h_change'])} ADA: {r['cardano']['usd']:,}$ ({r['cardano']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['dogecoin']['usd_24h_change'])} DOGE: {r['dogecoin']['usd']:,}$ ({r['dogecoin']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['polkadot']['usd_24h_change'])} DOT: {r['polkadot']['usd']:,}$ ({r['polkadot']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['litecoin']['usd_24h_change'])} LTC: {r['litecoin']['usd']:,}$ ({r['litecoin']['usd_24h_change']:.1f}%)\n"
            f"{arrow(r['chainlink']['usd_24h_change'])} LINK: {r['chainlink']['usd']:,}$ ({r['chainlink']['usd_24h_change']:.1f}%)\n"
        )
    except Exception as e:
        return f"تعذر جلب أسعار العملات الرقمية: {e}"

def get_metals():
    try:
        metals = {
            'XAU': ('🥇', 'الذهب'),
            'XAG': ('🥈', 'الفضة'),
            'XPT': ('⚪', 'البلاتين'),
            'XPD': ('🔘', 'البلاديوم'),
        }
        result = "⚗️ أسعار المعادن الثمينة:\n\n"
        for symbol, (emoji, name) in metals.items():
            try:
                r = requests.get(
                    f"https://api.gold-api.com/price/{symbol}",
                    timeout=10
                ).json()
                price = r.get('price', 'غير متوفر')
                result += f"{emoji} {name}: {price}$ للأونصة\n"
            except:
                result += f"{emoji} {name}: غير متوفر حالياً\n"
        return result
    except Exception as e:
        return f"تعذر جلب أسعار المعادن: {e}"

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
            'KWD': '🇰🇼 الدينار الكويتي',
            'BHD': '🇧🇭 الدينار البحريني',
            'QAR': '🇶🇦 الريال القطري',
            'OMR': '🇴🇲 الريال العماني',
            'JOD': '🇯🇴 الدينار الأردني',
            'IQD': '🇮🇶 الدينار العراقي',
            'LBP': '🇱🇧 الليرة اللبنانية',
            'SYP': '🇸🇾 الليرة السورية',
            'YER': '🇾🇪 الريال اليمني',
            'DZD': '🇩🇿 الدينار الجزائري',
            'MAD': '🇲🇦 الدرهم المغربي',
            'TND': '🇹🇳 الدينار التونسي',
            'LYD': '🇱🇾 الدينار الليبي',
            'SDG': '🇸🇩 الجنيه السوداني',
            'SOS': '🇸🇴 الشلن الصومالي',
            'DJF': '🇩🇯 الفرنك الجيبوتي',
            'KMF': '🇰🇲 الفرنك القمري',
            'MRU': '🇲🇷 الأوقية الموريتانية',
            'ILS': '🇵🇸 الشيكل الفلسطيني',
            'EUR': '🇪🇺 اليورو',
            'GBP': '🇬🇧 الجنيه الإسترليني',
        }

        arabic = (
            f"🌍 العملات العربية:\n"
            f"🇸🇦 ريال سعودي: {rates.get('SAR', 'N/A')}\n"
            f"🇦🇪 درهم إماراتي: {rates.get('AED', 'N/A')}\n"
            f"🇪🇬 جنيه مصري: {rates.get('EGP', 'N/A')}\n"
            f"🇰🇼 دينار كويتي: {rates.get('KWD', 'N/A')}\n"
            f"🇧🇭 دينار بحريني: {rates.get('BHD', 'N/A')}\n"
            f"🇶🇦 ريال قطري: {rates.get('QAR', 'N/A')}\n"
            f"🇴🇲 ريال عماني: {rates.get('OMR', 'N/A')}\n"
            f"🇯🇴 دينار أردني: {rates.get('JOD', 'N/A')}\n"
            f"🇱🇧 ليرة لبنانية: {rates.get('LBP', 'N/A')}\n"
            f"🇮🇶 دينار عراقي: {rates.get('IQD', 'N/A')}\n"
            f"🇸🇾 ليرة سورية: {rates.get('SYP', 'N/A')}\n"
            f"🇾🇪 ريال يمني: {rates.get('YER', 'N/A')}\n"
            f"🇩🇿 دينار جزائري: {rates.get('DZD', 'N/A')}\n"
            f"🇲🇦 درهم مغربي: {rates.get('MAD', 'N/A')}\n"
            f"🇹🇳 دينار تونسي: {rates.get('TND', 'N/A')}\n"
            f"🇱🇾 دينار ليبي: {rates.get('LYD', 'N/A')}\n"
            f"🇸🇩 جنيه سوداني: {rates.get('SDG', 'N/A')}\n"
            f"🇸🇴 شلن صومالي: {rates.get('SOS', 'N/A')}\n"
            f"🇩🇯 فرنك جيبوتي: {rates.get('DJF', 'N/A')}\n"
            f"🇰🇲 فرنك قمري: {rates.get('KMF', 'N/A')}\n"
            f"🇲🇷 أوقية موريتانية: {rates.get('MRU', 'N/A')}\n"
            f"🇵🇸 شيكل فلسطيني: {rates.get('ILS', 'N/A')}\n"
        )

        foreign = (
            f"\n🌐 العملات الأجنبية:\n"
            f"🇺🇸 دولار أمريكي: {rates.get('USD', 'N/A')}\n"
            f"🇪🇺 يورو: {rates.get('EUR', 'N/A')}\n"
            f"🇬🇧 جنيه إسترليني: {rates.get('GBP', 'N/A')}\n"
            f"🇨🇭 فرنك سويسري: {rates.get('CHF', 'N/A')}\n"
            f"🇯🇵 ين ياباني: {rates.get('JPY', 'N/A')}\n"
            f"🇨🇳 يوان صيني: {rates.get('CNY', 'N/A')}\n"
            f"🇨🇦 دولار كندي: {rates.get('CAD', 'N/A')}\n"
            f"🇦🇺 دولار أسترالي: {rates.get('AUD', 'N/A')}\n"
            f"🇮🇳 روبية هندية: {rates.get('INR', 'N/A')}\n"
            f"🇹🇷 ليرة تركية: {rates.get('TRY', 'N/A')}\n"
            f"🇷🇺 روبل روسي: {rates.get('RUB', 'N/A')}\n"
            f"🇰🇷 وون كوري: {rates.get('KRW', 'N/A')}\n"
            f"🇧🇷 ريال برازيلي: {rates.get('BRL', 'N/A')}\n"
            f"🇸🇬 دولار سنغافوري: {rates.get('SGD', 'N/A')}\n"
            f"🇭🇰 دولار هونج كونج: {rates.get('HKD', 'N/A')}\n"
            f"🇳🇿 دولار نيوزيلندي: {rates.get('NZD', 'N/A')}\n"
            f"🇳🇴 كرون نرويجي: {rates.get('NOK', 'N/A')}\n"
            f"🇸🇪 كرون سويدي: {rates.get('SEK', 'N/A')}\n"
            f"🇩🇰 كرون دنماركي: {rates.get('DKK', 'N/A')}\n"
            f"🇲🇽 بيزو مكسيكي: {rates.get('MXN', 'N/A')}\n"
            f"🇿🇦 راند جنوب أفريقي: {rates.get('ZAR', 'N/A')}\n"
            f"🇵🇰 روبية باكستانية: {rates.get('PKR', 'N/A')}\n"
            f"🇮🇩 روبية إندونيسية: {rates.get('IDR', 'N/A')}\n"
            f"🇹🇭 بات تايلاندي: {rates.get('THB', 'N/A')}\n"
            f"🇵🇱 زلوتي بولندي: {rates.get('PLN', 'N/A')}\n"
            f"🇲🇾 رينغيت ماليزي: {rates.get('MYR', 'N/A')}\n"
            f"🇵🇭 بيزو فلبيني: {rates.get('PHP', 'N/A')}\n"
            f"🇳🇬 نايرة نيجيرية: {rates.get('NGN', 'N/A')}\n"
            f"🇰🇪 شلن كيني: {rates.get('KES', 'N/A')}\n"
            f"🇦🇷 بيزو أرجنتيني: {rates.get('ARS', 'N/A')}\n"
            f"🇨🇴 بيزو كولومبي: {rates.get('COP', 'N/A')}\n"
            f"🇨🇱 بيزو تشيلي: {rates.get('CLP', 'N/A')}\n"
        )

        return (
            f"💵 أسعار الصرف مقابل {base_names.get(base, base)}:\n\n"
            + arabic + foreign
        )

    except Exception as e:
        return f"تعذر جلب أسعار الصرف: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
        [InlineKeyboardButton("⚗️ المعادن الثمينة", callback_data='metals')],
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

    elif query.data == 'metals':
        await query.message.reply_text("⏳ جاري جلب أسعار المعادن...")
        await query.message.reply_text(get_metals())

    elif query.data == 'currency_menu':
        keyboard1 = [
            [InlineKeyboardButton("🇺🇸 مقابل الدولار", callback_data='cur_USD')],
            [InlineKeyboardButton("🇸🇦 مقابل الريال السعودي", callback_data='cur_SAR')],
            [InlineKeyboardButton("🇦🇪 مقابل الدرهم الإماراتي", callback_data='cur_AED')],
            [InlineKeyboardButton("🇪🇬 مقابل الجنيه المصري", callback_data='cur_EGP')],
            [InlineKeyboardButton("🇰🇼 مقابل الدينار الكويتي", callback_data='cur_KWD')],
            [InlineKeyboardButton("🇧🇭 مقابل الدينار البحريني", callback_data='cur_BHD')],
            [InlineKeyboardButton("🇶🇦 مقابل الريال القطري", callback_data='cur_QAR')],
            [InlineKeyboardButton("🇴🇲 مقابل الريال العماني", callback_data='cur_OMR')],
            [InlineKeyboardButton("🇯🇴 مقابل الدينار الأردني", callback_data='cur_JOD')],
            [InlineKeyboardButton("🇱🇧 مقابل الليرة اللبنانية", callback_data='cur_LBP')],
            [InlineKeyboardButton("🇮🇶 مقابل الدينار العراقي", callback_data='cur_IQD')],
            [InlineKeyboardButton("🇸🇾 مقابل الليرة السورية", callback_data='cur_SYP')],
            [InlineKeyboardButton("🇾🇪 مقابل الريال اليمني", callback_data='cur_YER')],
            [InlineKeyboardButton("🇩🇿 مقابل الدينار الجزائري", callback_data='cur_DZD')],
            [InlineKeyboardButton("🇲🇦 مقابل الدرهم المغربي", callback_data='cur_MAD')],
            [InlineKeyboardButton("🇹🇳 مقابل الدينار التونسي", callback_data='cur_TND')],
            [InlineKeyboardButton("🇱🇾 مقابل الدينار الليبي", callback_data='cur_LYD')],
            [InlineKeyboardButton("🇸🇩 مقابل الجنيه السوداني", callback_data='cur_SDG')],
            [InlineKeyboardButton("🇸🇴 مقابل الشلن الصومالي", callback_data='cur_SOS')],
            [InlineKeyboardButton("🇩🇯 مقابل الفرنك الجيبوتي", callback_data='cur_DJF')],
            [InlineKeyboardButton("🇰🇲 مقابل الفرنك القمري", callback_data='cur_KMF')],
            [InlineKeyboardButton("🇲🇷 مقابل الأوقية الموريتانية", callback_data='cur_MRU')],
            [InlineKeyboardButton("🇵🇸 مقابل الشيكل الفلسطيني", callback_data='cur_ILS')],
            [InlineKeyboardButton("🇪🇺 مقابل اليورو", callback_data='cur_EUR')],
            [InlineKeyboardButton("🇬🇧 مقابل الجنيه الإسترليني", callback_data='cur_GBP')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
        ]
        await query.message.reply_text(
            "اختر العملة الأساسية للمقارنة:",
            reply_markup=InlineKeyboardMarkup(keyboard1)
        )

    elif query.data.startswith('cur_'):
        base = query.data.replace('cur_', '')
        await query.message.reply_text("⏳ جاري جلب الأسعار...")
        await query.message.reply_text(get_currency(base))

    elif query.data.startswith('all_'):
        base = query.data.replace('all_', '')
        await query.message.reply_text("⏳ جاري جلب كل الأسعار...")
        await query.message.reply_text(get_crypto())
        await query.message.reply_text(get_metals())
        await query.message.reply_text(get_currency(base))

    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
            [InlineKeyboardButton("⚗️ المعادن الثمينة", callback_data='metals')],
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
