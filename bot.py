import telebot
import yt_dlp
import os
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ЗАМЕНИ НА ТВОЙ ТОКЕН

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Пришли ссылку на видео с YouTube!\n\nПример:\nhttps://youtu.be/dQw4w9WgXcQ")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    # Проверяем, что это ссылка на YouTube
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.match(youtube_regex, url)
    
    if not match:
        bot.reply_to(message, "❌ Это не похоже на ссылку YouTube!\nПожалуйста, отправь ссылку в формате:\nhttps://youtu.be/ID_видео")
        return
    
    msg = bot.reply_to(message, "⏳ Ищу видео...")

    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'prefer_insecure': True,
        'user_agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.71 Mobile Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Скачиваем видео
            info = ydl.extract_info(url, download=True)
            
            # Проверяем, что видео найдено
            if info is None:
                bot.reply_to(message, "❌ Не удалось найти видео по этой ссылке.\nПроверь ссылку и попробуй снова.")
                return
                
            filename = f"video.{info['ext']}"
            
            # Проверяем, что файл создался
            if not os.path.exists(filename):
                bot.reply_to(message, "❌ Не удалось скачать видео. Попробуй другую ссылку.")
                return
        
        # Отправляем видео
        with open(filename, 'rb') as f:
            bot.send_video(
                message.chat.id, 
                f, 
                caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')[:100]}"
            )
        
        # Удаляем файл
        os.remove(filename)
        
    except Exception as e:
        error_text = str(e)
        if "Sign in to confirm" in error_text:
            bot.reply_to(message, "⚠️ YouTube временно блокирует скачивание.\n\nПопробуй через 10-15 минут.")
        else:
            bot.reply_to(message, f"❌ Ошибка: {error_text[:200]}\n\nПопробуй другую ссылку.")

bot.polling()
