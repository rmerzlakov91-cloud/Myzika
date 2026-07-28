import telebot
import yt_dlp
import os

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ЗАМЕНИ НА ТВОЙ ТОКЕН

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Пришли ссылку на видео с YouTube!")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    msg = bot.reply_to(message, "⏳ Ищу видео...")

    # Опции для скачивания БЕЗ кук
    ydl_opts = {
        'format': 'best[height<=720]',  # Качество 720p
        'outtmpl': 'video.%(ext)s',    # Имя файла
        'quiet': True,                  # Не писать лишнего в логи
        'no_warnings': True,            # Не показывать предупреждения
        'extract_flat': False,          # Полная информация о видео
        'ignoreerrors': True,           # Игнорировать ошибки
        'no_check_certificate': True,   # Не проверять сертификат
        'prefer_insecure': True,        # Использовать http если https не работает
    }

    try:
        # Пробуем скачать
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"video.{info['ext']}"
            
        # Отправляем видео
        with open(filename, 'rb') as f:
            bot.send_video(
                message.chat.id, 
                f, 
                caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')}"
            )
        
        # Удаляем файл
        os.remove(filename)
        
    except Exception as e:
        error_text = str(e)
        # Если ошибка про куки или бота
        if "Sign in to confirm" in error_text or "bot" in error_text:
            bot.reply_to(message, "⚠️ YouTube временно блокирует скачивание.\n\nПопробуй:\n1️⃣ Отправить другое видео\n2️⃣ Подождать 5-10 минут\n3️⃣ Отправить ссылку на короткое видео (до 3 минут)")
        else:
            bot.reply_to(message, f"❌ Ошибка: {error_text[:200]}")

bot.polling()
