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
    
    # ОЧИЩАЕМ ССЫЛКУ ОТ ЛИШНЕГО (убираем всё после & или ?)
    clean_url = re.sub(r'[&?].*$', '', url)
    
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
            # Пробуем скачать
            info = ydl.extract_info(clean_url, download=True)
            
            # ЕСЛИ НЕ НАШЛО ВИДЕО — ПЫТАЕМСЯ НАЙТИ ПО ID
            if info is None:
                # Извлекаем ID видео из ссылки
                video_id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', clean_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    # Пробуем скачать через прямую ссылку на ID
                    fallback_url = f"https://www.youtube.com/watch?v={video_id}"
                    info = ydl.extract_info(fallback_url, download=True)
                    
                    if info is None:
                        raise Exception("Видео не найдено")
                else:
                    raise Exception("Неверный формат ссылки")
            
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
                "2️⃣ Подождать 10-15 минут\n"
                "3️⃣ Отправить ссылку на короткое видео (до 3 минут)",
                message.chat.id, msg.message_id
            )
        elif "NoneType" in error_text or "not found" in error_text.lower():
            bot.edit_message_text(
                "🔍 Не удалось найти видео по этой ссылке.\n\n"
                "Попробуй:\n"
                "1️⃣ Скопировать ссылку заново (через кнопку 'Поделиться')\n"
                "2️⃣ Отправить ссылку в формате: https://youtu.be/ID_видео\n"
                "3️⃣ Найти другое видео",
                message.chat.id, msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Ошибка: {error_text[:150]}\n\n"
                "Попробуй другую ссылку или подожди.",
                message.chat.id, msg.message_id
            )

bot.polling()
