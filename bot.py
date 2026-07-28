import telebot
import yt_dlp
import os

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Замени на свой токен от @BotFather

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Пришли ссылку на видео с YouTube — я скачаю!")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    bot.reply_to(message, "⏳ Скачиваю...")

    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': 'video.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"video.{info['ext']}"

        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption=f"✅ Готово!\nНазвание: {info.get('title', 'Без названия')}")

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

bot.polling()
