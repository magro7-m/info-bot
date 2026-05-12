import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, 
    CallbackQueryHandler, ContextTypes
)

# ═══════════════════════════════
#         الإعدادات
# ═══════════════════════════════
TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')

# قائمة المشتركين المدفوعين
PAID_USERS = set()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ═══════════════════════════════
#      جلب المعلومات تلقائياً
# ═══════════════════════════════
def get_gold_price():
    """جلب سعر الذهب"""
    try:
        url = "https://api.metals.live/v1/spot/gold"
        response = requests.get(url, timeout=10)
        data = response.json()
        price = data[0].get('price', 'غير متوفر')
        return f"🥇 سعر الذهب: {price}$ للأونصة"
    except:
        return "🥇 سعر الذهب: غير متوفر حالياً"

def get_crypto_prices():
    """جلب أسعار العملات الرقمية"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        btc = data['bitcoin']
        eth = data['ethereum']
        bnb = data['binancecoin']
        
        def arrow(change):
            return "📈" if change > 0 else "📉"
        
        return f"""
💰 أسعار العملات الرقمية:

{arrow(btc['usd_24h_change'])} BTC: {btc['usd']:,.0f}$ ({btc['usd_24h_change']:.1f}%)
{arrow(eth['usd_24h_change'])} ETH: {eth['usd']:,.0f}$ ({eth['usd_24h_change']:.1f}%)
{arrow(bnb['usd_24h_change'])} BNB: {bnb['usd']:,.0f}$ ({bnb['usd_24h_change']:.1f}%)
"""
    except:
        return "💰 أسعار العملات: غير متوفرة حالياً"

def get_currency_rates():
    """جلب أسعار صرف العملات"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        rates = data['rates']
        
        return f"""
💵 أسعار الصرف مقابل الدولار:

🇸🇦 ريال سعودي: {rates.get('SAR', 'N/A')}
🇦🇪 درهم إماراتي: {rates.get('AED', 'N/A')}
🇪🇬 جنيه مصري: {rates.get('EGP', 'N/A')}
🇪🇺 يورو: {rates.get('EUR', 'N/A')}
🇬🇧 جنيه إسترليني: {rates.get('GBP', 'N/A')}
"""
    except:
        return "💵 أسعار الصرف: غير متوفرة حالياً"

def build_daily_report():
    """بناء التقرير اليومي الكامل"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""
📊 التقرير اليومي الشامل
🕐 {now}
{'='*30}

{get_crypto_prices()}
{'='*30}

{get_gold_price()}
{'='*30}

{get_currency_rates()}
{'='*30}

📱 بوت المعلومات المالية
    """
    return report

# ═══════════════════════════════
#        أوامر البوت
# ═══════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    keyboard = [
        [InlineKeyboardButton("📊 التقرير اليومي", callback_data='report')],
        [InlineKeyboardButton("💰 أسعار العملات", callback_data='crypto')],
        [InlineKeyboardButton("💵 أسعار الصرف", callback_data='currency')],
        [InlineKeyboardButton("🥇 سعر الذهب", callback_data='gold')],
        [InlineKeyboardButton("⭐ اشترك بالنسخة المميزة", callback_data='subscribe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 مرحباً بك في بوت المعلومات المالية!\n\n"
        "أحصل على آخر الأسعار والمعلومات الاقتصادية\n"
        "بشكل تلقائي ومجاني!\n\n"
        "اختر ما تريد:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'report':
        await query.message.reply_text(
            "⏳ جاري تجميع المعلومات..."
        )
        report = build_daily_report()
        await query.message.reply_text(report)
    
    elif query.data == 'crypto':
        await query.message.reply_text(get_crypto_prices())
    
    elif query.data == 'currency':
        await query.message.reply_text(get_currency_rates())
    
    elif query.data == 'gold':
        await query.message.reply_text(get_gold_price())
    
    elif query.data == 'subscribe':
        await query.message.reply_text(
            "⭐ النسخة المميزة\n\n"
            "✅ تقارير يومية تلقائية\n"
            "✅ تنبيهات فورية\n"
            "✅ تحليلات متقدمة\n\n"
            "💰 السعر: 5$ شهرياً\n\n"
            "للاشتراك تواصل مع المشرف"
        )

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    """إرسال التقرير اليومي تلقائياً"""
    report = build_daily_report()
    for user_id in PAID_USERS:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=report
            )
        except Exception as e:
            log.error(f"خطأ في الإرسال: {e}")

# ═══════════════════════════════
#        تشغيل البوت
# ═══════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # إرسال تقرير يومي تلقائي الساعة 8 صباحاً
    app.job_queue.run_daily(
        send_daily_report,
        time=datetime.strptime("08:00", "%H:%M").time()
    )
    
    log.info("✅ البوت يعمل!")
    app.run_polling()

if __name__ == "__main__":
    main()
