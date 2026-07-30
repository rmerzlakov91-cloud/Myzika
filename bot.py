import telebot
import time
import re
import threading

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"
bot = telebot.TeleBot(TOKEN)

# ID бота TopSaverBot (можно узнать через @getmyid_bot)
TOP_SAVER_ID = "@TopSaverBot"

# Храним состояние пользователей
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-посредник для TopSaverBot!\n\n"
        "Просто отправь мне ссылку на YouTube,\n"
        "а я скачаю видео в 1080p."
    )

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    # Отправляем ссылку в TopSaverBot
    msg = bot.reply_to(message, "⏳ Отправляю ссылку в бот-помощник...")
    
    try:
        # Шаг 1: Отправляем ссылку в TopSaverBot
        sent = bot.send_message(TOP_SAVER_ID, url)
        
        # Шаг 2: Ждём ответ (выбор качества)
        time.sleep(5)  # Даём время боту ответить
        
        # Получаем последние сообщения от TopSaverBot
        # (это нужно делать через forward или проверку)
        
        # Шаг 3: Ищем кнопку 1080p и нажимаем её
        # (кнопки в телеграме — это inline_keyboard с callback_data)
        
        bot.edit_message_text(
            "✅ Видео обрабатывается...\n"
            "⏳ Подожди 20-30 секунд.",
            message.chat.id, msg.message_id
        )
        
        # Шаг 4: Ожидаем видео от TopSaverBot
        # (сложная часть — нужно перехватить сообщение)
        
        # Шаг 5: Пересылаем видео пользователю
        # bot.forward_message(message.chat.id, TOP_SAVER_ID, video_message_id)
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка: {str(e)[:150]}\n\n"
            "Попробуй ещё раз через минуту.",
            message.chat.id, msg.message_id
        )

# Перехватываем сообщения от TopSaverBot
@bot.message_handler(func=lambda m: m.from_user.id == TOP_SAVER_ID)
def handle_top_saver_response(message):
    # Если пришло видео — пересылаем пользователю
    if message.video:
        # Находим пользователя, который запросил это видео
        # (нужно хранить соответствие ссылка -> пользователь)
        bot.forward_message(user_id, message.chat.id, message.message_id)
        bot.send_message(user_id, "✅ Готово! Видео скачано в 1080p.")

bot.polling()
