import telegram
import random
import time
import requests
from threading import Thread
from telegram.ext import Updater, CommandHandler

# === КОНФІГУРАЦІЯ ===
# ВАШ ТОКЕН ВСТАВЛЕНО СЮДИ:
TOKEN = '7680522904:AAFzLxiVWnOB9vJqI6qOX7Fru6VlTk7KSRw' 

# Глобальний набір для зберігання ID підписників
SUBSCRIBERS = set() 

broadcast_bot = telegram.Bot(token=TOKEN)

def get_top_100_symbols():
    """Отримує символи 100 найбільших криптовалют з CoinGecko."""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false')
        response.raise_for_status() 
        data = response.json()
        symbols = [f"{coin['symbol'].upper()}/USDT" for coin in data]
        return symbols
    except Exception:
        return ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]

def generate_signal():
    """Генерує випадковий, ІМІТОВАНИЙ сигнал."""
    symbols = get_top_100_symbols()
    asset = random.choice(symbols)
    direction = random.choice(["LONG", "SHORT"])
    leverage = random.randint(20, 40)
    entry_price = round(random.uniform(0.5, 50000), 2)
    
    message = (
        f"🚨 **ІМІТОВАНИЙ НАВЧАЛЬНИЙ СИГНАЛ** 🚨\n\n"
        f"**АКТИВ:** `{asset}`\n"
        f"**НАПРЯМОК:** **{direction}**\n"
        f"**ПЛЕЧЕ:** **{leverage}x**\n"
        f"**ЦІНА ВХОДУ (Entry):** $\n`{entry_price}`\n\n"
        f"Це імітація для навчального проєкту. **НЕ ВИКОРИСТОВУЙТЕ ДЛЯ РЕАЛЬНОЇ ТОРГІВЛІ!**"
    )
    return message

def start(update, context):
    chat_id = update.message.chat_id
    SUBSCRIBERS.add(chat_id)
    print(f"Новий підписник: {chat_id}. Загальна кількість: {len(SUBSCRIBERS)}")
    update.message.reply_text(
        'Вітаємо! Ви підписані на імітовані сигнали для навчального проєкту.'
    )

def stop_subscription(update, context):
    chat_id = update.message.chat_id
    if chat_id in SUBSCRIBERS:
        SUBSCRIBERS.discard(chat_id)
        update.message.reply_text("Ви успішно відписалися від розсилки.")

def send_signal_task():
    """Цикл для надсилання сигналів кожному підписнику."""
    while True:
        delay_minutes = random.randint(12, 60)
        print(f"Наступний сигнал через {delay_minutes} хвилин...")
        time.sleep(delay_minutes * 60)
        
        signal_text = generate_signal()
        
        for subscriber_id in list(SUBSCRIBERS):
            try:
                broadcast_bot.send_message(
                    chat_id=subscriber_id, 
                    text=signal_text, 
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
            except telegram.error.Unauthorized:
                SUBSCRIBERS.discard(subscriber_id)

        if SUBSCRIBERS:
            print(f"Сигнал надіслано {len(SUBSCRIBERS)} підписникам о {time.strftime('%H:%M:%S')}")


if __name__ == '__main__':
    print("Бот запущено. Налаштовуємо слухачі команд...")
    
    signal_thread = Thread(target=send_signal_task, daemon=True)
    signal_thread.start()
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop_subscription))
    
    print("Бот готовий приймати команди...")
    updater.start_polling()
    updater.idle()
