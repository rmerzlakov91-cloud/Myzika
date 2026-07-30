import telebot
import yt_dlp
import os
import re
import time

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Получи у @BotFather

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-скачивалка!\n\n"
        "Просто отправь мне ссылку на YouTube,\n"
        "и я скачаю видео и отправлю его тебе!"
    )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    msg = bot.reply_to(message, "⏳ Начинаю скачивание... Подожди немного.")
    
    # Очищаем ссылку от лишнего
    clean_url = re.sub(r'[&?].*$', '', url)
    
    # Настройки для скачивания
    ydl_opts = {
        'format': 'best[height<=720]',  # Качество до 720p
        'outtmpl': 'video.%(ext)s',     # Имя файла
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extract_flat': False,
        'force_generic_extractor': False,
        'cookies': None,  # Не используем куки
        'nocheckcertificate': True,
        'prefer_insecure': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Пробуем скачать
            info = ydl.extract_info(clean_url, download=True)
            
            # Проверяем, что видео найдено
            if info is None:
                # Пробуем через ID
                video_id = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', clean_url)
                if video_id:
                    video_id = video_id.group(1)
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            
            if info is None:
                bot.edit_message_text(
                    "❌ Не удалось найти видео.\n"
                    "Попробуй другую ссылку.",
                    message.chat.id, msg.message_id
                )
                return
            
            filename = f"video.{info['ext']}"
            
            # Проверяем, что файл создался
            if not os.path.exists(filename):
                bot.edit_message_text(
                    "❌ Не удалось скачать видео.\n"
                    "Попробуй другую ссылку.",
                    message.chat.id, msg.message_id
                )
                return
        
        # Отправляем видео в Telegram
        with open(filename, 'rb') as f:
            bot.send_video(
                message.chat.id,
                f,
                caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')[:100]}",
                supports_streaming=True
            )
        
        # Удаляем файл после отправки
        os.remove(filename)
        
    except Exception as e:
        error_text = str(e)
        
        # Обрабатываем разные ошибки
        if "Sign in to confirm" in error_text:
            bot.edit_message_text(
                "⚠️ YouTube блокирует скачивание.\n\n"
                "Попробуй:\n"
                "1️⃣ Другую ссылку\n"
                "2️⃣ Подождать 10-15 минут\n"
                "3️⃣ Видео покороче (до 5 минут)",
                message.chat.id, msg.message_id
            )
        elif "ffmpeg" in error_text.lower():
            bot.edit_message_text(
                "⚠️ Ошибка с обработкой видео.\n"
                "Попробуй другую ссылку.",
                message.chat.id, msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Ошибка: {error_text[:150]}\n\n"
                "Попробуй другую ссылку или подожди.",
                message.chat.id, msg.message_id
            )

bot.polling()
