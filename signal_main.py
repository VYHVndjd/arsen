import telebot
from telebot import types
import random
import os

# Твій токен
API_TOKEN = '8584033541:AAHd4M5g7hNZ0_K5krbNg5vF8K-7fo0AJD0'

bot = telebot.TeleBot(API_TOKEN)

# --- БАЗА ДАНИХ (Тимчасова, в пам'яті) ---
user_data = {}  # Зберігає налаштування: {user_id: {'lang': 'ua', 'pair': 'EUR/USD'}}

# --- ТЕКСТИ ТА ПЕРЕКЛАДИ ---
TEXTS = {
    'ua': {
        'welcome': "Привіт! Оберіть мову:",
        'menu_btn': "📊 Отримати сигнал",
        'choose_pair': "Оберіть валютну пару:",
        'choose_time': "Оберіть час експірації:",
        'analyzing': "⏳ Аналізую ринок...",
        'signal_res': "Сигнал для",
        'action_up': "🟢 ВГОРУ (BUY)",
        'action_down': "🔴 ВНИЗ (SELL)",
        'lang_set': "Мову встановлено: Українська 🇺🇦"
    },
    'ru': {
        'welcome': "Привет! Выберите язык:",
        'menu_btn': "📊 Получить сигнал",
        'choose_pair': "Выберите валютную пару:",
        'choose_time': "Выберите время экспирации:",
        'analyzing': "⏳ Анализирую рынок...",
        'signal_res': "Сигнал для",
        'action_up': "🟢 ВВЕРХ (BUY)",
        'action_down': "🔴 ВНИЗ (SELL)",
        'lang_set': "Язык установлен: Русский 🇷🇺"
    },
    'en': {
        'welcome': "Hello! Choose language:",
        'menu_btn': "📊 Get Signal",
        'choose_pair': "Choose currency pair:",
        'choose_time': "Choose expiration time:",
        'analyzing': "⏳ Analyzing market...",
        'signal_res': "Signal for",
        'action_up': "🟢 UP (BUY)",
        'action_down': "🔴 DOWN (SELL)",
        'lang_set': "Language set: English 🇬🇧"
    }
}

# --- СПИСКИ ---
CURRENCY_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"
]

TIMES = ["5 min", "10 min", "15 min"]

# --- ЛОГІКА БОТА ---

# 1. Старт і вибір мови
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_ua = types.InlineKeyboardButton("Українська 🇺🇦", callback_data='lang_ua')
    btn_ru = types.InlineKeyboardButton("Русский 🇷🇺", callback_data='lang_ru')
    btn_en = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
    markup.add(btn_en, btn_ru, btn_ua)
    
    bot.send_message(message.chat.id, "Please choose your language / Оберіть мову:", reply_markup=markup)

# Обробка вибору мови
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang_code = call.data.split('_')[1] # ua, ru або en
    chat_id = call.message.chat.id
    
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['lang'] = lang_code
    
    bot.delete_message(chat_id, call.message.message_id)
    
    text_dict = TEXTS[lang_code]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_signal = types.KeyboardButton(text_dict['menu_btn'])
    markup.add(item_signal)
    
    bot.send_message(chat_id, text_dict['lang_set'], reply_markup=markup)

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

# 3. Вибір валютної пари
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
    for time in TIMES:
        buttons.append(types.InlineKeyboardButton(time, callback_data=f'time_{time}'))
    markup.add(*buttons)
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, 
                          text=texts['choose_time'], reply_markup=markup)

# Обробка вибору часу і видача сигналу
@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def callback_time(call):
    chat_id = call.message.chat.id
    time_val = call.data.split('_')[1]
    
    user_lang = user_data.get(chat_id, {}).get('lang', 'en')
    texts = TEXTS[user_lang]
    pair = user_data[chat_id].get('temp_pair', 'Unknown')
    
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                          text=texts['analyzing'])
    
    direction = random.choice([texts['action_up'], texts['action_down']])
    
    result_text = (
        f"📊 <b>{texts['signal_res']} {pair}</b>\n"
        f"⏱ <b>{time_val}</b>\n"
        f"-------------------\n"
        f"{direction}\n"
        f"-------------------"
    )
    
    bot.send_message(chat_id, result_text, parse_mode='HTML')

# Запуск
if __name__ == '__main__':
    bot.infinity_polling()
