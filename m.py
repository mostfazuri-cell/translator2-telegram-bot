import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import aiohttp
import json

# تنظیمات
#TOKEN = '7949645373:AAHQFJAHkCJUhU6qebzV0Y25wfAzUIjZy-0'
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# دیکشنری برای ذخیره انتخاب‌های موقت کاربران
user_choices = {}

# دیکشنری زبان‌ها
LANGUAGES = {
    'fa': 'فارسی',
    'en': 'انگلیسی',
    'ar': 'عربی',
    'tr': 'ترکی',
    'de': 'آلمانی',
    'fr': 'فرانسوی',
    'es': 'اسپانیایی',
    'ru': 'روسی',
    'zh-cn': 'چینی',
    'ja': 'ژاپنی',
    'ko': 'کره‌ای',
    'it': 'ایتالیایی',
    'hi': 'هندی',
    'pt': 'پرتغالی',
    'nl': 'هلندی',
    'pl': 'لهستانی',
    'uk': 'اوکراینی',
    'he': 'عبری',
    'sv': 'سوئدی',
    'da': 'دانمارکی',
    'fi': 'فنلاندی',
    'no': 'نروژی',
    'cs': 'چکی',
    'el': 'یونانی'
}

# تابع ترجمه با استفاده از Google Translate API
async def translate_text(text, dest_lang):
    """ترجمه متن به زبان مقصد"""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',  # تشخیص خودکار زبان مبدأ
            'tl': dest_lang,  # زبان مقصد
            'dt': 't',
            'q': text
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # استخراج متن ترجمه شده
                    translated_text = ''.join([item[0] for item in data[0] if item[0]])
                    
                    # تشخیص زبان مبدأ
                    src_lang = data[2] if len(data) > 2 else 'auto'
                    
                    return {
                        'text': translated_text,
                        'src': src_lang,
                        'dest': dest_lang
                    }
                else:
                    return None
    except Exception as e:
        print(f"خطا در ترجمه: {e}")
        return None

# تابع تشخیص زبان
async def detect_language(text):
    """تشخیص زبان متن"""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': 'en',  # ترجمه به انگلیسی برای تشخیص
            'dt': 't',
            'q': text[:100]  # فقط ۱۰۰ کاراکتر اول برای تشخیص
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[2] if len(data) > 2 else 'en'
                else:
                    return 'en'
    except:
        return 'en'

# تابع sync برای استفاده در telebot
def sync_translate(text, dest_lang):
    """تابع همگام برای ترجمه"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(translate_text(text, dest_lang))
        return result
    finally:
        loop.close()

def sync_detect(text):
    """تابع همگام برای تشخیص زبان"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(detect_language(text))
        return result
    finally:
        loop.close()

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """🤖 **ربات مترجم هوشمند**

✨ **ایجاد شده توسط: نورالله نوری**
📅 **نسخه: ۲.۰ با رابط کاربری پیشرفته**

📌 **نحوه استفاده آسان:**
۱. متن خود را ارسال کنید
۲. زبان مقصد را از بین دکمه‌ها انتخاب کنید

🎯 **ویژگی‌ها:**
• ترجمه به ۱۵۰+ زبان
• رابط کاربری دکمه‌ای
• تشخیص خودکار زبان مبدأ
• سرعت بالا و دقیق

برای شروع، یک متن ارسال کنید..."""
    
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """📚 **راهنمای کامل:**

🔹 **روش اول (ترجمه سریع):**
۱. متن خود را ارسال کنید
۲. از صفحه باز شده، زبان مقصد را انتخاب کنید

🔹 **روش دوم (انتخاب زبان اول):**
از دکمه‌های زیر استفاده کنید:

🔹 **دستورات:**
/start - راهنمای اولیه
/help - این راهنما
/langs - لیست کامل زبان‌ها
/translate - ترجمه مستقیم

🔹 **پشتیبانی:**
برای گزارش مشکل یا پیشنهاد:
@YourUsername"""
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['langs'])
def show_all_languages(message):
    langs_text = "🌍 **زبان‌های پشتیبانی شده:**\n\n"
    for code, name in LANGUAGES.items():
        langs_text += f"• {code}: {name}\n"
    
    langs_text += "\n📌 **برای استفاده:** متن ارسال کنید و از دکمه‌ها زبان را انتخاب نمایید."
    bot.send_message(message.chat.id, langs_text)

@bot.message_handler(commands=['translate'])
def start_translation(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇺🇸 انگلیسی", callback_data="lang_en"),
        InlineKeyboardButton("🇸🇦 عربی", callback_data="lang_ar"),
        InlineKeyboardButton("🇹🇷 ترکی", callback_data="lang_tr")
    )
    keyboard.add(
        InlineKeyboardButton("🇩🇪 آلمانی", callback_data="lang_de"),
        InlineKeyboardButton("🇫🇷 فرانسوی", callback_data="lang_fr"),
        InlineKeyboardButton("🇪🇸 اسپانیایی", callback_data="lang_es"),
        InlineKeyboardButton("🇷🇺 روسی", callback_data="lang_ru")
    )
    keyboard.add(
        InlineKeyboardButton("📋 سایر زبان‌ها", callback_data="more_langs"),
        InlineKeyboardButton("❌ لغو", callback_data="cancel")
    )
    
    bot.send_message(
        message.chat.id,
        "🌍 **لطفا زبان مقصد را انتخاب کنید:**\n\nسپس متن خود را ارسال نمایید.",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    user_choices[user_id] = {
        'text': message.text,
        'step': 'waiting_for_lang'
    }
    
    keyboard = create_lang_keyboard()
    
    bot.send_message(
        message.chat.id,
        f"📝 **متن شما دریافت شد:**\n`{message.text[:100]}{'...' if len(message.text) > 100 else ''}`\n\n"
        "🌍 **لطفا زبان مقصد را انتخاب کنید:**",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

def create_lang_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    keyboard.add(
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="translate_fa"),
        InlineKeyboardButton("🇺🇸 انگلیسی", callback_data="translate_en"),
        InlineKeyboardButton("🇸🇦 عربی", callback_data="translate_ar")
    )
    
    keyboard.add(
        InlineKeyboardButton("🇹🇷 ترکی", callback_data="translate_tr"),
        InlineKeyboardButton("🇩🇪 آلمانی", callback_data="translate_de"),
        InlineKeyboardButton("🇫🇷 فرانسوی", callback_data="translate_fr")
    )
    
    keyboard.add(
        InlineKeyboardButton("🇪🇸 اسپانیایی", callback_data="translate_es"),
        InlineKeyboardButton("🇷🇺 روسی", callback_data="translate_ru"),
        InlineKeyboardButton("🇯🇵 ژاپنی", callback_data="translate_ja")
    )
    
    keyboard.add(
        InlineKeyboardButton("🇨🇳 چینی", callback_data="translate_zh-cn"),
        InlineKeyboardButton("🇰🇷 کره‌ای", callback_data="translate_ko"),
        InlineKeyboardButton("🇮🇹 ایتالیایی", callback_data="translate_it")
    )
    
    keyboard.add(
        InlineKeyboardButton("📚 سایر زبان‌ها", callback_data="show_more"),
        InlineKeyboardButton("🔍 تشخیص خودکار", callback_data="auto_detect"),
        InlineKeyboardButton("❌ لغو", callback_data="cancel_translate")
    )
    
    return keyboard

def create_extended_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    extended_langs = {
        'hi': '🇮🇳 هندی',
        'pt': '🇵🇹 پرتغالی',
        'nl': '🇳🇱 هلندی',
        'pl': '🇵🇱 لهستانی',
        'uk': '🇺🇦 اوکراینی',
        'he': '🇮🇱 عبری',
        'sv': '🇸🇪 سوئدی',
        'da': '🇩🇰 دانمارکی',
        'fi': '🇫🇮 فنلاندی',
        'no': '🇳🇴 نروژی',
        'cs': '🇨🇿 چکی',
        'el': '🇬🇷 یونانی'
    }
    
    buttons = []
    for code, name in extended_langs.items():
        buttons.append(InlineKeyboardButton(name, callback_data=f"translate_{code}"))
    
    for i in range(0, len(buttons), 2):
        if i+1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.add(
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"),
        InlineKeyboardButton("❌ لغو", callback_data="cancel_translate")
    )
    
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        if call.data.startswith('translate_'):
            lang_code = call.data.replace('translate_', '')
            
            if user_id in user_choices and 'text' in user_choices[user_id]:
                text_to_translate = user_choices[user_id]['text']
                
                # انجام ترجمه
                result = sync_translate(text_to_translate, lang_code)
                
                if result:
                    src_lang_name = LANGUAGES.get(result['src'], 'ناشناخته')
                    dest_lang_name = LANGUAGES.get(lang_code, 'ناشناخته')
                    
                    response = f"""✅ **ترجمه تکمیل شد:**

📝 **متن اصلی:**
`{text_to_translate}`

🔤 **زبان مبدأ:** {src_lang_name}
🎯 **زبان مقصد:** {dest_lang_name}

📖 **ترجمه شده:**
`{result['text']}`

✍️ **ایجاد شده توسط نورالله نوری**"""
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=response,
                        parse_mode='Markdown'
                    )
                    
                    if user_id in user_choices:
                        del user_choices[user_id]
                else:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="⚠️ **خطا در ترجمه.**\n\nلطفاً دوباره تلاش کنید یا از متن کوتاه‌تری استفاده نمایید.",
                        parse_mode='Markdown'
                    )
            
            else:
                bot.answer_callback_query(call.id, "⚠️ لطفا ابتدا متن خود را ارسال کنید.")
        
        elif call.data == 'show_more':
            keyboard = create_extended_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🌐 **زبان‌های بیشتر:**\n\nلطفا زبان مورد نظر را انتخاب کنید:",
                reply_markup=keyboard
            )
        
        elif call.data == 'auto_detect':
            if user_id in user_choices and 'text' in user_choices[user_id]:
                text_to_translate = user_choices[user_id]['text']
                
                # تشخیص زبان
                detected_lang = sync_detect(text_to_translate)
                
                # تصمیم برای ترجمه
                if detected_lang == 'fa':
                    dest_lang = 'en'
                else:
                    dest_lang = 'fa'
                
                # ترجمه
                result = sync_translate(text_to_translate, dest_lang)
                
                if result:
                    detected_lang_name = LANGUAGES.get(detected_lang, 'ناشناخته')
                    dest_lang_name = LANGUAGES.get(dest_lang, 'ناشناخته')
                    
                    response = f"""🤖 **ترجمه خودکار:**

📝 **متن اصلی:** `{text_to_translate}`
🔍 **زبان شناسایی شده:** {detected_lang_name}
🎯 **زبان مقصد:** {dest_lang_name}
📖 **ترجمه:** `{result['text']}`

✍️ **ایجاد شده توسط نورالله نوری**"""
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=response,
                        parse_mode='Markdown'
                    )
                else:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="⚠️ **خطا در ترجمه خودکار.**",
                        parse_mode='Markdown'
                    )
        
        elif call.data == 'back_to_main':
            keyboard = create_lang_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🌍 **لطفا زبان مقصد را انتخاب کنید:**",
                reply_markup=keyboard
            )
        
        elif call.data in ['cancel', 'cancel_translate']:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ **عملیات لغو شد.**\n\nبرای شروع مجدد، یک متن جدید ارسال کنید.",
                reply_markup=None
            )
            
            if user_id in user_choices:
                del user_choices[user_id]
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"⚠️ خطا: {str(e)[:50]}")

# اجرا
print("=" * 50)
print("🤖 ربات مترجم با رابط کاربری دکمه‌ای")
print("👨‍💻 ایجاد شده توسط: نورالله نوری")
print("🚀 در حال اجرا...")
print("=" * 50)
bot.polling()