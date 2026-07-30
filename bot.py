import telebot
import time

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Замени на свой
bot = telebot.TeleBot(TOKEN)

YOUR_SECOND_ACCOUNT_ID = 7199949032  # ID твоего второго аккаунта
user_requests = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Отправь мне ссылку на YouTube,\n"
        "и я скачаю видео через 1-2 минуты."
    )

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка!")
        return
    
    user_id = message.chat.id
    user_requests[user_id] = {'url': url, 'status': 'waiting'}
    
    bot.send_message(
        YOUR_SECOND_ACCOUNT_ID, 
        f"🔗 {url}"
    )
    
    bot.reply_to(message, 
        "⏳ Ссылка отправлена на скачивание.\n"
        "Подожди 1-2 минуты."
    )

# Принимаем ВСЕ видео (от кого угодно)
@bot.message_handler(content_types=['video'])
def handle_video(message):
    # Проверяем, есть ли пользователи, которые ждут видео
    waiting_users = [uid for uid, data in user_requests.items() if data['status'] == 'waiting']
    
    if not waiting_users:
        bot.reply_to(message, "❌ Нет активных запросов на скачивание.")
        return
    
    # Отправляем видео первому в очереди
    user_id = waiting_users[0]
    
    # Отправляем видео пользователю
    bot.send_video(
        user_id, 
        message.video.file_id, 
        caption="✅ Видео готово!"
    )
    
    # Отмечаем, что видео отправлено
    user_requests[user_id]['status'] = 'done'
    
    # Отвечаем отправителю видео (второму аккаунту)
    bot.reply_to(message, f"✅ Видео отправлено пользователю {user_id}")

bot.polling()
