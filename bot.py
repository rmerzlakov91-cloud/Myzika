import telebot
import requests
import json
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ЗАМЕНИ НА СВОЙ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-помощник!\n\n"
        "Отправь мне ссылку на видео с YouTube, TikTok, Instagram или других сайтов.\n"
        "Я найду ссылку для скачивания!"
    )

@bot.message_handler(func=lambda m: True)
def get_download_link(message):
    url = message.text.strip()
    
    # Проверяем, что это ссылка
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Отправь ссылку на видео!")
        return
    
    msg = bot.reply_to(message, "⏳ Ищу ссылки...")
    
    try:
        # Используем бесплатный API от SaveFrom
        api_url = "https://api.savefrom.net/2/"
        params = {
            'url': url,
            'ajax': 1,
            'lang': 'ru'
        }
        
        response = requests.get(api_url, params=params, timeout=20)
        data = response.json()
        
        # Проверяем, что ответ пришёл
        if 'result' not in data or 'files' not in data['result']:
            bot.edit_message_text(
                "❌ Не удалось найти ссылки для этого видео.\n\n"
                "Попробуй:\n"
                "1️⃣ Другую ссылку\n"
                "2️⃣ Видео с YouTube (они лучше всего работают)\n"
                "3️⃣ Подожди 1-2 минуты и попробуй снова",
                message.chat.id, msg.message_id
            )
            return
        
        files = data['result']['files']
        
        # Формируем ответ со ссылками
        reply = "✅ Найдены ссылки для скачивания:\n\n"
        count = 0
        
        for quality, info in files.items():
            if 'link' in info:
                link = info['link']
                quality_label = info.get('quality_label', quality)
                reply += f"📹 {quality_label}: {link}\n"
                count += 1
                if count >= 5:  # Ограничиваем до 5 ссылок
                    break
        
        if count == 0:
            bot.edit_message_text(
                "❌ Не удалось получить ссылки. Попробуй другое видео.",
                message.chat.id, msg.message_id
            )
            return
        
        reply += "\n📌 Скопируй ссылку и открой в браузере для скачивания!"
        bot.edit_message_text(reply, message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка: {str(e)[:150]}\n\n"
            "Попробуй:\n"
            "1️⃣ Другую ссылку\n"
            "2️⃣ Видео с YouTube\n"
            "3️⃣ Подожди и попробуй снова",
            message.chat.id, msg.message_id
        )

bot.polling()
