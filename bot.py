import telebot
import yt_dlp
import os

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на YouTube, и я скачаю видео.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    msg = bot.reply_to(message, "⏳ Начинаю скачивание... Подожди немного.")
    
    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 60,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"video.{info['ext']}"
        
        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')[:100]}")
        os.remove(filename)
        
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)[:150]}", message.chat.id, msg.message_id)

bot.polling()
