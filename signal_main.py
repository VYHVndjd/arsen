import telebot
from telebot import types
import random
import time

# Твій токен
API_TOKEN = '8584033541:AAHd4M5g7hNZ0_K5krbNg5vF8K-7fo0AJD0'

bot = telebot.TeleBot(API_TOKEN)

# --- БАЗА ДАНИХ (Тимчасова, в пам'яті) ---
user_data = {}

# --- ПОСИЛАННЯ ---
REGISTER_LINK = "https://u3.shortink.io/register?utm_campaign=833673&utm_source=affiliate&utm_medium=sr&a=RqqZmq3RiEnldX&ac=aitrendmaster&code=50START"

# --- ТЕКСТИ ТА ПЕРЕКЛАДИ ---
TEXTS = {
    'ua': {
        # Переклад вітання
        'welcome_body': (
            "⚡ <b>Ласкаво просимо до AiTrendMaster</b>\n\n"
            "Виконайте ці швидкі кроки для активації доступу:\n"
            f"1️⃣ Зареєструйтесь за <a href='{REGISTER_LINK}'>офіційним посиланням</a>\n"
            "2️⃣ Зробіть перший депозит\n"
            "3️⃣ Налаштуйте валютну пару та почніть торгувати"
        ),
        'menu_btn': "📊 Отримати сигнал",
        'choose_pair': "Оберіть крипто-пару:",
        'choose_time': "Оберіть час експірації:",
        'analyzing': "⏳ <b>Аналізую ринок...</b>\n\nЦе може зайняти декілька секунд...",
        'signal_res': "Сигнал для",
        'action_up': "🟢 ВГОРУ (LONG)",
        'action_down': "🔴 ВНИЗ (SHORT)",
        'lang_set': "Мову встановлено: Українська 🇺🇦"
    },
    'ru': {
        # Переклад вітання
        'welcome_body': (
            "⚡ <b>Добро пожаловать в AiTrendMaster</b>\n\n"
            "Выполните эти быстрые шаги для активации доступа:\n"
            f"1️⃣ Зарегистрируйтесь по <a href='{REGISTER_LINK}'>официальной ссылке</a>\n"
            "2️⃣ Сделайте первый депозит\n"
            "3️⃣ Настройте валютную пару и начните торговать"
        ),
        'menu_btn': "📊 Получить сигнал",
        'choose_pair': "Выберите крипто-пару:",
        'choose_time': "Выберите время экспирации:",
        'analyzing': "⏳ <b>Анализирую рынок...</b>\n\nЭто может занять несколько секунд...",
        'signal_res': "Сигнал для",
        'action_up': "🟢 ВВЕРХ (LONG)",
        'action_down': "🔴 ВНИЗ (SHORT)",
        'lang_set': "Язык установлен: Русский 🇷🇺"
    },
    'en': {
        # Оригінал вітання
        'welcome_body': (
            "⚡ <b>Welcome to AiTrendMaster</b>\n\n"
            "Follow these quick steps to activate your access:\n"
            f"1️⃣ Sign up using our <a href='{REGISTER_LINK}'>official link</a>\n"
            "2️⃣ Make your first deposit\n"
            "3️⃣ Set up a currency pair and start trading"
        ),
        'menu_btn': "📊 Get Signal",
        'choose_pair': "Choose crypto pair:",
        'choose_time': "Choose expiration time:",
        'analyzing': "⏳ <b>Analyzing market...</b>\n\nPlease wait a few seconds...",
        'signal_res': "Signal for",
        'action_up': "🟢 UP (LONG)",
        'action_down': "🔴 DOWN (SHORT)",
        'lang_set': "Language set: English 🇬🇧"
    }
}

# --- СПИСКИ ---
CURRENCY_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT",
    "SOL/USDT", "LTC/USDT", "ADA/USDT", "DOGE/USDT"
]

TIMES = ["5 sec", "10 sec", "15 sec"]

# --- ЛОГІКА БОТА ---

# 1. Старт і вибір мови
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_ua = types.InlineKeyboardButton("Українська 🇺🇦", callback_data='lang_ua')
    btn_ru = types.InlineKeyboardButton("Русский 🇷🇺", callback_data='lang_ru')
    btn_en = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
    markup.add(btn_en, btn_ru, btn_ua)
    
    bot.send_message(message.chat.id, "Please choose your language / Выберите язык:", reply_markup=markup)

# Обробка вибору мови
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang_code = call.data.split('_')[1]
    chat_id = call.message.chat.id
    
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['lang'] = lang_code
    
    # Видаляємо повідомлення з вибором мови
    bot.delete_message(chat_id, call.message.message_id)
    
    text_dict = TEXTS[lang_code]
    
    # Створюємо клавіатуру меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_signal = types.KeyboardButton(text_dict['menu_btn'])
    markup.add(item_signal)
    
    # Відправляємо ВІТАЛЬНЕ ПОВІДОМЛЕННЯ
    # disable_web_page_preview=False --> Вмикає відображення картинки сайту
    bot.send_message(
        chat_id, 
        text_dict['welcome_body'], 
        parse_mode='HTML', 
        disable_web_page_preview=False, 
        reply_markup=markup
    )

# 2. Натискання кнопки "Отримати сигнал"
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_lang = user_data.get(chat_id, {}).get('lang', 'en')
    texts = TEXTS[user_lang]

    if message.text in [TEXTS['ua']['menu_btn'], TEXTS['ru']['menu_btn'], TEXTS['en']['menu_btn']]:
        show_pairs(chat_id, texts)
    else:
        bot.send_message(chat_id, "Type /start to restart.")

# 3. Вибір пари
def show_pairs(chat_id, texts):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for pair in CURRENCY_PAIRS:
        buttons.append(types.InlineKeyboardButton(pair, callback_data=f'pair_{pair}'))
    markup.add(*buttons)
    
    bot.send_message(chat_id, texts['choose_pair'], reply_markup=markup)

# Обробка вибору пари
@bot.callback_query_handler(func=lambda call: call.data.startswith('pair_'))
def callback_pair(call):
    chat_id = call.message.chat.id
    pair = call.data.split('_')[1]
    
    user_data[chat_id]['temp_pair'] = pair
    user_lang = user_data.get(chat_id, {}).get('lang', 'en')
    texts = TEXTS[user_lang]
    
    show_time(call.message, texts)

# 4. Вибір часу
def show_time(message, texts):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for time_val in TIMES:
        buttons.append(types.InlineKeyboardButton(time_val, callback_data=f'time_{time_val}'))
    markup.add(*buttons)
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                          text=texts['choose_time'], reply_markup=markup)

# Обробка вибору часу і видача сигналу (З ЗАТРИМКОЮ 5 сек)
@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def callback_time(call):
    chat_id = call.message.chat.id
    time_val = call.data.split('_')[1]
    
    user_lang = user_data.get(chat_id, {}).get('lang', 'en')
    texts = TEXTS[user_lang]
    pair = user_data[chat_id].get('temp_pair', 'Unknown')
    
    # 1. Змінюємо текст на "Аналізую..."
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                          text=texts['analyzing'], parse_mode='HTML')
    
    # 2. Робимо паузу 5 секунд
    time.sleep(5)
    
    # 3. Генеруємо сигнал
    direction = random.choice([texts['action_up'], texts['action_down']])
    
    result_text = (
        f"📊 <b>{texts['signal_res']} {pair}</b>\n"
        f"⏱ <b>{time_val}</b>\n"
        f"-------------------\n"
        f"{direction}\n"
        f"-------------------"
    )
    
    # 4. Редагуємо повідомлення на результат
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                          text=result_text, parse_mode='HTML')

# Запуск
if __name__ == '__main__':
    bot.infinity_polling()
