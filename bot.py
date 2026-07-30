import telebot
import time

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Замени на свой (получи у @BotFather)
bot = telebot.TeleBot(TOKEN)

# ID твоего второго аккаунта (куда будем отправлять ссылки)
YOUR_SECOND_ACCOUNT_ID = 7199949032

# Храним пользователей, которые ждут видео
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
    
    # Отправляем ссылку твоему второму аккаунту
    bot.send_message(
        YOUR_SECOND_ACCOUNT_ID, 
        f"🔗 {url}"
    )
    
    bot.reply_to(message, 
        "⏳ Ссылка отправлена на скачивание.\n"
        "Подожди 1-2 минуты."
    )

# Получаем видео от UserBot-а (с твоего второго аккаунта)
@bot.message_handler(func=lambda m: m.chat.id == YOUR_SECOND_ACCOUNT_ID and m.video)
def handle_video(message):
    for user_id, data in user_requests.items():
        if data['status'] == 'waiting':
            bot.send_video(
                user_id, 
                message.video.file_id, 
                caption="✅ Видео готово!"
            )
            user_requests[user_id]['status'] = 'done'
            break

bot.polling()
