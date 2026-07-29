import telebot
import yt_dlp
import os
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ВСТАВЬ СВОЙ ТОКЕН

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-скачивалка!\n\n"
        "Отправь мне ссылку на YouTube, и я скачаю видео!"
    )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    msg = bot.reply_to(message, "⏳ Начинаю скачивание...")
    
    # Извлекаем ID видео из ссылки
    video_id = None
    id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
    if id_match:
        video_id = id_match.group(1)
    
    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extract_flat': False,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = None
            
            # СПОСОБ 1: Пробуем скачать по ID (самый надёжный)
            if video_id:
                try:
                    search_url = f"https://www.youtube.com/watch?v={video_id}"
                    info = ydl.extract_info(search_url, download=True)
                except:
                    pass
            
            # СПОСОБ 2: Если не получилось — пробуем через поиск
            if info is None:
                try:
                    # Ищем видео по ID через поиск
                    search_query = f"ytsearch1:{video_id}" if video_id else f"ytsearch1:{url}"
                    info = ydl.extract_info(search_query, download=True)
                except:
                    pass
            
            # СПОСОБ 3: Если всё плохо — пробуем через прямую ссылку
            if info is None:
                try:
                    info = ydl.extract_info(url, download=True)
                except:
                    pass
            
            # Если ничего не нашли — ошибка
            if info is None:
                raise Exception("Не удалось найти видео")
            
            filename = f"video.{info['ext']}"
        
        # Отправляем видео
        with open(filename, 'rb') as f:
            bot.send_video(
                message.chat.id, 
                f, 
                caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')[:100]}"
            )
        os.remove(filename)
        
    except Exception as e:
        error_text = str(e)
        
        if "Sign in to confirm" in error_text:
            bot.edit_message_text(
                "⚠️ YouTube временно блокирует скачивание.\n\n"
                "Попробуй:\n"
                "1️⃣ Другую ссылку\n"
                "2️⃣ Подождать 10-15 минут",
                message.chat.id, msg.message_id
            )
        elif "NoneType" in error_text or "not found" in error_text.lower():
            bot.edit_message_text(
                "🔍 Не удалось найти видео.\n\n"
                "Попробуй:\n"
                "1️⃣ Скопировать ссылку через кнопку 'Поделиться'\n"
                "2️⃣ Отправить ссылку на другое видео\n"
                "3️⃣ Написать /start и попробовать снова",
                message.chat.id, msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Ошибка: {error_text[:150]}\n\n"
                "Попробуй другую ссылку.",
                message.chat.id, msg.message_id
            )

bot.polling()
