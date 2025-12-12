import telegram
import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# === ВАШ ТОКЕН ===
TOKEN = '7680522904:AAFzLxiVWnOB9vJqI6qOX7Fru6VlTk7KSRw'

def start(update, context):
    """Викликається командою /start. Показує привітання та кнопку."""
    
    # Текст із ТЗ з вбудованим посиланням (Markdown)
    text = (
        "⚡ *Welcome to AiTrendMaster*\n\n"
        "Follow these quick steps to activate your access:\n"
        "1️⃣ Sign up using our [official link](https://u3.shortink.io/register?utm_campaign=833673&utm_source=affiliate&utm_medium=sr&a=RqqZmq3RiEnldX&ac=aitrendmaster&code=50START)\n"
        "2️⃣ Make your first deposit\n"
        "3️⃣ Set up a currency pair and start trading"
    )

    # Кнопка під текстом
    keyboard = [
        [InlineKeyboardButton("Отримати сигнали 📊", callback_data='get_signals')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Якщо це натискання кнопки "Назад", редагуємо старе повідомлення
    if update.callback_query:
        update.callback_query.edit_message_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    else:
        # Якщо це команда /start, надсилаємо нове
        update.message.reply_text(
            text=text, 
            reply_markup=reply_markup, 
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

def button_handler(update, context):
    """Обробляє натискання на кнопки."""
    query = update.callback_query
    query.answer() # Важливо, щоб кнопка перестала "крутитися"

    # Якщо натиснули "Отримати сигнали"
    if query.data == 'get_signals':
        keyboard = [
            [InlineKeyboardButton("BTC/USDT", callback_data='pair_BTC/USDT'), InlineKeyboardButton("ETH/USDT", callback_data='pair_ETH/USDT')],
            [InlineKeyboardButton("SOL/USDT", callback_data='pair_SOL/USDT'), InlineKeyboardButton("XRP/USDT", callback_data='pair_XRP/USDT')],
            [InlineKeyboardButton("BNB/USDT", callback_data='pair_BNB/USDT'), InlineKeyboardButton("LTC/USDT", callback_data='pair_LTC/USDT')],
            [InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="📉 *Оберіть валютну пару для аналізу:*",
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN
        )

    # Якщо натиснули "Назад"
    elif query.data == 'main_menu':
        start(update, context)

    # Якщо обрали конкретну пару (починається з 'pair_')
    elif query.data.startswith('pair_'):
        pair = query.data.split('_')[1] # Витягуємо назву пари, напр. BTC/USDT
        
        # Генеруємо сигнал
        signal_text = generate_signal(pair)
        
        # Додаємо кнопку "Назад" або "Інша пара"
        keyboard = [
            [InlineKeyboardButton("🔄 Інша пара", callback_data='get_signals')],
            [InlineKeyboardButton("🏠 Головне меню", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            text=signal_text,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN
        )

def generate_signal(pair):
    """Генерує текст сигналу для обраної пари."""
    direction = random.choice(["LONG 🟢", "SHORT 🔴"])
    leverage = random.choice([20, 25, 30, 50])
    
    # Генеруємо приблизну ціну (просто випадкові числа для імітації)
    # У реальному боті тут був би запит до API, але для імітації достатньо рандому
    if "BTC" in pair: entry = random.randint(95000, 99000)
    elif "ETH" in pair: entry = random.randint(2600, 2800)
    elif "SOL" in pair: entry = random.randint(180, 210)
    elif "BNB" in pair: entry = random.randint(600, 650)
    else: entry = random.uniform(0.5, 150)
    
    entry_price = round(entry, 2)
    
    # Розрахунок тейк-профітів
    tp1 = round(entry * (1.01 if "LONG" in direction else 0.99), 2)
    tp2 = round(entry * (1.02 if "LONG" in direction else 0.98), 2)
    sl = round(entry * (0.98 if "LONG" in direction else 1.02), 2)

    message = (
        f"📊 **ANALYTICS FOR {pair}**\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"💎 **Position:** {direction}\n"
        f"🚀 **Leverage:** Cross {leverage}x\n"
        f"💰 **Entry Price:** {entry_price}\n\n"
        f"🎯 **Targets:**\n"
        f"1️⃣ TP: {tp1}\n"
        f"2️⃣ TP: {tp2}\n\n"
        f"🛑 **Stop Loss:** {sl}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"⚠️ _Artificial Intelligence Analysis_"
    )
    return message

if __name__ == '__main__':
    # Створення Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    # Обробники команд
    dp.add_handler(CommandHandler("start", start))
    
    # Обробник натискання кнопок
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("Бот запущено...")
    
    # Запуск бота
    updater.start_polling()
    updater.idle()
