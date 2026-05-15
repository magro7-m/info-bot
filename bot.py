import os
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

user_calc_data = {}
user_alerts = {}
user_alert_setup = {}

ARABIC_CURRENCIES = {
    'SAR': '🇸🇦 ريال سعودي',
    'AED': '🇦🇪 درهم إماراتي',
    'EGP': '🇪🇬 جنيه مصري',
    'KWD': '🇰🇼 دينار كويتي',
    'BHD': '🇧🇭 دينار بحريني',
    'QAR': '🇶🇦 ريال قطري',
    'OMR': '🇴🇲 ريال عماني',
    'JOD': '🇯🇴 دينار أردني',
    'LBP': '🇱🇧 ليرة لبنانية',
    'IQD': '🇮🇶 دينار عراقي',
    'SYP': '🇸🇾 ليرة سورية',
    'YER': '🇾🇪 ريال يمني',
    'DZD': '🇩🇿 دينار جزائري',
    'MAD': '🇲🇦 درهم مغربي',
    'TND': '🇹🇳 دينار تونسي',
    'LYD': '🇱🇾 دينار ليبي',
    'SDG': '🇸🇩 جنيه سوداني',
    'SOS': '🇸🇴 شلن صومالي',
    'DJF': '🇩🇯 فرنك جيبوتي',
    'KMF': '🇰🇲 فرنك قمري',
    'MRU': '🇲🇷 أوقية موريتانية',
    'ILS': '🇵🇸 شيكل فلسطيني',
}

FOREIGN_CURRENCIES = {
    'USD': '🇺🇸 دولار أمريكي',
    'EUR': '🇪🇺 يورو',
    'GBP': '🇬🇧 جنيه إسترليني',
    'CHF': '🇨🇭 فرنك سويسري',
    'JPY': '🇯🇵 ين ياباني',
    'CNY': '🇨🇳 يوان صيني',
    'CAD': '🇨🇦 دولار كندي',
    'AUD': '🇦🇺 دولار أسترالي',
    'INR': '🇮🇳 روبية هندية',
    'TRY': '🇹🇷 ليرة تركية',
    'RUB': '🇷🇺 روبل روسي',
    'KRW': '🇰🇷 وون كوري',
    'BRL': '🇧🇷 ريال برازيلي',
    'SGD': '🇸🇬 دولار سنغافوري',
    'HKD': '🇭🇰 دولار هونج كونج',
    'NZD': '🇳🇿 دولار نيوزيلندي',
    'NOK': '🇳🇴 كرون نرويجي',
    'SEK': '🇸🇪 كرون سويدي',
    'MXN': '🇲🇽 بيزو مكسيكي',
    'ZAR': '🇿🇦 راند جنوب أفريقي',
    'PKR': '🇵🇰 روبية باكستانية',
    'MYR': '🇲🇾 رينغيت ماليزي',
    'THB': '🇹🇭 بات تايلاندي',
    'NGN': '🇳🇬 نايرة نيجيرية',
    'ARS': '🇦🇷 بيزو أرجنتيني',
}

ALL_CURRENCIES = {**ARABIC_CURRENCIES, **FOREIGN_CURRENCIES}

CRYPTO_LIST = {
    'bitcoin': 'BTC بيتكوين',
    'ethereum': 'ETH إيثيريوم',
    'binancecoin': 'BNB بينانس',
    'solana': 'SOL سولانا',
    'ripple': 'XRP ريبل',
}

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
        base_name = ALL_CURRENCIES.get(base, base)

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
            f"🇲🇾 رينغيت ماليزي: {rates.get('MYR', 'N/A')}\n"
            f"🇵🇭 بيزو فلبيني: {rates.get('PHP', 'N/A')}\n"
            f"🇳🇬 نايرة نيجيرية: {rates.get('NGN', 'N/A')}\n"
            f"🇦🇷 بيزو أرجنتيني: {rates.get('ARS', 'N/A')}\n"
            f"🇨🇴 بيزو كولومبي: {rates.get('COP', 'N/A')}\n"
            f"🇨🇱 بيزو تشيلي: {rates.get('CLP', 'N/A')}\n"
        )

        return f"💵 أسعار الصرف مقابل {base_name}:\n\n" + arabic + foreign

    except Exception as e:
        return f"تعذر جلب أسعار الصرف: {e}"

def calculate_conversion(amount, from_currency):
    try:
        r = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
            timeout=10
        ).json()
        rates = r['rates']
        from_name = ALL_CURRENCIES.get(from_currency, from_currency)
        result = f"🧮 تحويل {amount:,} {from_name}:\n\n"
        result += f"🌍 العملات العربية:\n"
        for code, name in ARABIC_CURRENCIES.items():
            if code != from_currency:
                converted = rates.get(code, 0) * amount
                result += f"{name}: {converted:,.2f}\n"
        result += f"\n🌐 العملات الأجنبية:\n"
        for code, name in FOREIGN_CURRENCIES.items():
            if code != from_currency:
                converted = rates.get(code, 0) * amount
                result += f"{name}: {converted:,.2f}\n"
        return result
    except Exception as e:
        return f"تعذر إجراء التحويل: {e}"

async def check_alerts(app):
    while True:
        try:
            if user_alerts:
                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': ','.join(CRYPTO_LIST.keys()),
                    'vs_currencies': 'usd'
                }
                prices = requests.get(url, params=params, timeout=10).json()

                alerts_to_remove = []
                for user_id, alerts in user_alerts.items():
                    for alert in alerts[:]:
                        coin = alert['coin']
                        target = alert['target']
                        direction = alert['direction']
                        current = prices.get(coin, {}).get('usd', 0)

                        triggered = (
                            (direction == 'above' and current >= target) or
                            (direction == 'below' and current <= target)
                        )

                        if triggered:
                            coin_name = CRYPTO_LIST.get(coin, coin)
                            direction_text = "وصل إلى أو تجاوز" if direction == 'above' else "انخفض إلى أو تحت"
                            msg = (
                                f"🔔 تنبيه السعر!\n\n"
                                f"💰 {coin_name}\n"
                                f"السعر الحالي: {current:,}$\n"
                                f"{direction_text} هدفك: {target:,}$"
                            )
                            try:
                                await app.bot.send_message(chat_id=user_id, text=msg)
                                alerts.remove(alert)
                            except Exception as e:
                                logging.error(f"خطأ في إرسال التنبيه: {e}")

        except Exception as e:
            logging.error(f"خطأ في فحص التنبيهات: {e}")

        await asyncio.sleep(60)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 العملات الرقمية", callback_data='crypto')],
        [InlineKeyboardButton("⚗️ المعادن الثمينة", callback_data='metals')],
        [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency_menu')],
        [InlineKeyboardButton("🧮 حاسبة تحويل العملات", callback_data='calc')],
        [InlineKeyboardButton("🔔 تنبيهات الأسعار", callback_data='alerts')],
        [InlineKeyboardButton("📊 كل الأسعار بالدولار", callback_data='all_USD')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً في بوت الخبير الاقتصادي!\n\n"
        "أحصل على آخر الأسعار والمعلومات الاقتصادية\n"
        "اختر ما تريد:",
        reply_markup=main_keyboard()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'crypto':
        await query.message.reply_text(get_crypto())

    elif query.data == 'metals':
        await query.message.reply_text("⏳ جاري جلب أسعار المعادن...")
        await query.message.reply_text(get_metals())

    elif query.data == 'alerts':
        keyboard = [
            [InlineKeyboardButton("🟠 بيتكوين BTC", callback_data='alert_bitcoin')],
            [InlineKeyboardButton("🔵 إيثيريوم ETH", callback_data='alert_ethereum')],
            [InlineKeyboardButton("🟡 بينانس BNB", callback_data='alert_binancecoin')],
            [InlineKeyboardButton("🟣 سولانا SOL", callback_data='alert_solana')],
            [InlineKeyboardButton("⚫ ريبل XRP", callback_data='alert_ripple')],
            [InlineKeyboardButton("📋 تنبيهاتي الحالية", callback_data='my_alerts')],
            [InlineKeyboardButton("🗑️ حذف كل التنبيهات", callback_data='clear_alerts')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
        ]
        await query.message.reply_text(
            "🔔 تنبيهات الأسعار\n\nاختر العملة التي تريد تنبيهاً عليها:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith('alert_'):
        coin = query.data.replace('alert_', '')
        user_alert_setup[user_id] = {'coin': coin, 'step': 'direction'}
        coin_name = CRYPTO_LIST.get(coin, coin)
        keyboard = [
            [InlineKeyboardButton("📈 عندما يرتفع فوق سعر معين", callback_data='dir_above')],
            [InlineKeyboardButton("📉 عندما ينخفض تحت سعر معين", callback_data='dir_below')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='alerts')]
        ]
        await query.message.reply_text(
            f"🔔 تنبيه لـ {coin_name}\nمتى تريد التنبيه؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in ['dir_above', 'dir_below']:
        if user_id in user_alert_setup:
            direction = 'above' if query.data == 'dir_above' else 'below'
            user_alert_setup[user_id]['direction'] = direction
            user_alert_setup[user_id]['step'] = 'price'
            direction_text = "ارتفع فوق" if direction == 'above' else "انخفض تحت"
            coin = user_alert_setup[user_id]['coin']
            coin_name = CRYPTO_LIST.get(coin, coin)
            await query.message.reply_text(
                f"💰 أدخل السعر المستهدف بالدولار لـ {coin_name}\n"
                f"سيصلك تنبيه عندما {direction_text} هذا السعر\n\n"
                f"مثال: 90000"
            )

    elif query.data == 'my_alerts':
        alerts = user_alerts.get(user_id, [])
        if not alerts:
            await query.message.reply_text("📭 لا توجد تنبيهات مفعّلة حالياً")
        else:
            msg = "📋 تنبيهاتك الحالية:\n\n"
            for i, alert in enumerate(alerts, 1):
                coin_name = CRYPTO_LIST.get(alert['coin'], alert['coin'])
                direction_text = "فوق" if alert['direction'] == 'above' else "تحت"
                msg += f"{i}. {coin_name} {direction_text} {alert['target']:,}$\n"
            await query.message.reply_text(msg)

    elif query.data == 'clear_alerts':
        user_alerts.pop(user_id, None)
        await query.message.reply_text("✅ تم حذف جميع تنبيهاتك")

    elif query.data == 'currency_menu':
        keyboard = [
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
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'calc':
        keyboard = [
            [InlineKeyboardButton("🇺🇸 دولار أمريكي", callback_data='calc_USD'),
             InlineKeyboardButton("🇸🇦 ريال سعودي", callback_data='calc_SAR')],
            [InlineKeyboardButton("🇦🇪 درهم إماراتي", callback_data='calc_AED'),
             InlineKeyboardButton("🇪🇬 جنيه مصري", callback_data='calc_EGP')],
            [InlineKeyboardButton("🇰🇼 دينار كويتي", callback_data='calc_KWD'),
             InlineKeyboardButton("🇶🇦 ريال قطري", callback_data='calc_QAR')],
            [InlineKeyboardButton("🇧🇭 دينار بحريني", callback_data='calc_BHD'),
             InlineKeyboardButton("🇴🇲 ريال عماني", callback_data='calc_OMR')],
            [InlineKeyboardButton("🇯🇴 دينار أردني", callback_data='calc_JOD'),
             InlineKeyboardButton("🇱🇧 ليرة لبنانية", callback_data='calc_LBP')],
            [InlineKeyboardButton("🇮🇶 دينار عراقي", callback_data='calc_IQD'),
             InlineKeyboardButton("🇸🇾 ليرة سورية", callback_data='calc_SYP')],
            [InlineKeyboardButton("🇾🇪 ريال يمني", callback_data='calc_YER'),
             InlineKeyboardButton("🇩🇿 دينار جزائري", callback_data='calc_DZD')],
            [InlineKeyboardButton("🇲🇦 درهم مغربي", callback_data='calc_MAD'),
             InlineKeyboardButton("🇹🇳 دينار تونسي", callback_data='calc_TND')],
            [InlineKeyboardButton("🇱🇾 دينار ليبي", callback_data='calc_LYD'),
             InlineKeyboardButton("🇸🇩 جنيه سوداني", callback_data='calc_SDG')],
            [InlineKeyboardButton("🇸🇴 شلن صومالي", callback_data='calc_SOS'),
             InlineKeyboardButton("🇲🇷 أوقية موريتانية", callback_data='calc_MRU')],
            [InlineKeyboardButton("🇵🇸 شيكل فلسطيني", callback_data='calc_ILS'),
             InlineKeyboardButton("🇩🇯 فرنك جيبوتي", callback_data='calc_DJF')],
            [InlineKeyboardButton("🇪🇺 يورو", callback_data='calc_EUR'),
             InlineKeyboardButton("🇬🇧 جنيه إسترليني", callback_data='calc_GBP')],
            [InlineKeyboardButton("🇨🇭 فرنك سويسري", callback_data='calc_CHF'),
             InlineKeyboardButton("🇯🇵 ين ياباني", callback_data='calc_JPY')],
            [InlineKeyboardButton("🇨🇳 يوان صيني", callback_data='calc_CNY'),
             InlineKeyboardButton("🇹🇷 ليرة تركية", callback_data='calc_TRY')],
            [InlineKeyboardButton("🇷🇺 روبل روسي", callback_data='calc_RUB'),
             InlineKeyboardButton("🇮🇳 روبية هندية", callback_data='calc_INR')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
        ]
        await query.message.reply_text(
            "🧮 حاسبة تحويل العملات\n\nاختر العملة التي تريد التحويل منها:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith('calc_'):
        currency = query.data.replace('calc_', '')
        user_calc_data[user_id] = {'type': 'calc', 'currency': currency}
        currency_name = ALL_CURRENCIES.get(currency, currency)
        await query.message.reply_text(
            f"💱 أدخل المبلغ بـ {currency_name}:\n\nمثال: 100 أو 1500.50"
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
        await query.message.reply_text(
            "اختر ما تريد:",
            reply_markup=main_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id in user_alert_setup and user_alert_setup[user_id].get('step') == 'price':
        try:
            target_price = float(text.replace(',', ''))
            setup = user_alert_setup[user_id]
            coin = setup['coin']
            direction = setup['direction']
            coin_name = CRYPTO_LIST.get(coin, coin)
            direction_text = "فوق" if direction == 'above' else "تحت"

            if user_id not in user_alerts:
                user_alerts[user_id] = []

            user_alerts[user_id].append({
                'coin': coin,
                'target': target_price,
                'direction': direction
            })

            del user_alert_setup[user_id]

            await update.message.reply_text(
                f"✅ تم تفعيل التنبيه!\n\n"
                f"💰 {coin_name}\n"
                f"سيصلك تنبيه عندما يكون السعر {direction_text} {target_price:,}$\n\n"
                f"يتم الفحص كل دقيقة 🔍",
                reply_markup=main_keyboard()
            )
        except ValueError:
            await update.message.reply_text(
                "⚠️ الرجاء إدخال رقم صحيح فقط\nمثال: 90000"
            )

    elif user_id in user_calc_data and user_calc_data[user_id].get('type') == 'calc':
        try:
            amount = float(text.replace(',', ''))
            currency = user_calc_data[user_id]['currency']
            await update.message.reply_text("⏳ جاري حساب التحويل...")
            result = calculate_conversion(amount, currency)
            await update.message.reply_text(result)
            del user_calc_data[user_id]
            await update.message.reply_text(
                "اختر ما تريد:",
                reply_markup=main_keyboard()
            )
        except ValueError:
            await update.message.reply_text(
                "⚠️ الرجاء إدخال رقم صحيح فقط\nمثال: 100 أو 1500.50"
            )

async def post_init(app):
    asyncio.create_task(check_alerts(app))

def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
