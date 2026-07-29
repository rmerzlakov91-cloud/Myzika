import telebot
import yt_dlp
import os

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ВСТАВЬ СВОЙ ТОКЕН

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-скачивалка!\n\n"
        "Отправь мне ссылку на YouTube, и я скачаю видео!\n"
        "Поддерживаются любые ссылки с YouTube."
    )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    msg = bot.reply_to(message, "⏳ Начинаю скачивание...")
    
    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
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
                "3️⃣ Видео покороче (до 3 минут)",
                message.chat.id, msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Ошибка: {error_text[:150]}\n\n"
                "Попробуй другую ссылку или подожди.",
                message.chat.id, msg.message_id
            )

bot.polling()
