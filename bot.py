import telebot
import requests
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ЗАМЕНИ НА СВОЙ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-скачивалка!\n\n"
        "Отправь мне ссылку на видео с YouTube, TikTok, Instagram или других сайтов.\n"
        "Я найду ссылку для скачивания!"
    )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    # Проверяем, что это ссылка
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Отправь ссылку на видео!")
        return
    
    msg = bot.reply_to(message, "⏳ Ищу ссылку для скачивания...")
    
    try:
        # Используем API от SaveFrom (бесплатно, без регистрации)
        api_url = "https://api.savefrom.net/2/"
        params = {
            'url': url,
            'ajax': 1,
            'lang': 'ru'
        }
        
        response = requests.get(api_url, params=params, timeout=30)
        data = response.json()
        
        if 'result' in data and 'files' in data['result']:
            files = data['result']['files']
            download_links = []
            
            # Собираем все доступные ссылки
            for quality, info in files.items():
                if 'link' in info:
                    link = info['link']
                    quality_text = info.get('quality_label', quality)
                    download_links.append(f"[{quality_text}] {link}")
            
            if download_links:
                reply = "✅ Найдены ссылки для скачивания:\n\n"
                reply += "\n".join(download_links[:5])  # Не больше 5 ссылок
                reply += "\n\n📌 Просто открой ссылку в браузере и сохрани видео!"
                
                bot.edit_message_text(reply, message.chat.id, msg.message_id)
            else:
                bot.edit_message_text("❌ Ссылки не найдены. Попробуй другое видео.", 
                                    message.chat.id, msg.message_id)
        else:
            error_msg = data.get('error', 'Не удалось найти ссылки')
            bot.edit_message_text(f"❌ Ошибка: {error_msg}\n\nПопробуй другую ссылку.", 
                                message.chat.id, msg.message_id)
                                
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)[:150]}\n\nПопробуй другую ссылку.", 
                            message.chat.id, msg.message_id)

bot.polling()
