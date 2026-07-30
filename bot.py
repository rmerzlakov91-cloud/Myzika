import os
import telebot
import yt_dlp
import re

BOT_TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Вставь сюда свой токен

bot = telebot.TeleBot(BOT_TOKEN)

# Очищаем ссылку от лишнего
def clean_url(url):
    return re.sub(r'[&?].*$', '', url)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на YouTube, и я скачаю видео.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "Это не ссылка. Отправь правильную ссылку на YouTube.")
        return

    msg = bot.reply_to(message, "⏳ Начинаю скачивание... Подожди немного.")
    clean_url = clean_url(url)

    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'cookies': None,
        'nocheckcertificate': True,
        'prefer_insecure': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            if info is None:
                video_id = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', clean_url)
                if video_id:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id.group(1)}", download=True)
            if info is None:
                bot.edit_message_text("❌ Не удалось найти видео.", message.chat.id, msg.message_id)
                return
            filename = f"video.{info['ext']}"
            if not os.path.exists(filename):
                bot.edit_message_text("❌ Не удалось скачать видео.", message.chat.id, msg.message_id)
                return

        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption=f"✅ Готово!\n📹 {info.get('title', 'Без названия')[:100]}", supports_streaming=True)
        os.remove(filename)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)[:150]}\nПопробуй другую ссылку.", message.chat.id, msg.message_id)

bot.polling()
