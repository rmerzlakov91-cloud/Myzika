import telebot
import yt_dlp
import os
import requests
import json
import time

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
    
    # ПРОБУЕМ СПОСОБ 1: Прямое скачивание (yt-dlp)
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
        return  # Если скачалось, выходим
        
    except Exception as e:
        error_text = str(e)
        
        # Если ошибка "Sign in" — пробуем способ 2
        if "Sign in to confirm" in error_text or "bot" in error_text:
            bot.edit_message_text("⏳ YouTube блокирует, пробую другой способ...", 
                                message.chat.id, msg.message_id)
            time.sleep(2)
        else:
            # Другая ошибка — пробуем через SaveFrom
            bot.edit_message_text("⏳ Пробую через сайт-помощник...", 
                                message.chat.id, msg.message_id)
            time.sleep(2)
    
    # СПОСОБ 2: Через SaveFrom API
    try:
        api_url = "https://api.savefrom.net/2/"
        params = {
            'url': url,
            'ajax': 1,
            'lang': 'ru'
        }
        
        response = requests.get(api_url, params=params, timeout=20)
        data = response.json()
        
        if 'result' in data and 'files' in data['result']:
            files = data['result']['files']
            
            # Берём ссылку на лучшее качество
            download_link = None
            best_quality = 0
            
            for quality, info in files.items():
                if 'link' in info:
                    if 'quality_label' in info and info['quality_label']:
                        # Парсим качество (например, "720p" → 720)
                        try:
                            q = int(re.search(r'(\d+)p', info['quality_label']).group(1))
                            if q > best_quality:
                                best_quality = q
                                download_link = info['link']
                        except:
                            download_link = info['link']
                    else:
                        download_link = info['link']
            
            if download_link:
                bot.edit_message_text(
                    f"✅ Нашёл ссылку для скачивания!\n\n"
                    f"🔗 Ссылка:\n{download_link}\n\n"
                    "📌 Открой её в браузере, чтобы сохранить видео!",
                    message.chat.id, msg.message_id
                )
                return
                
    except Exception as e2:
        pass  # Если не получилось — переходим к способу 3
    
    # СПОСОБ 3: Если ничего не работает — просим попробовать позже
    bot.edit_message_text(
        "❌ Не удалось скачать видео.\n\n"
        "Попробуй:\n"
        "1️⃣ Отправить ссылку на другое видео\n"
        "2️⃣ Подождать 5-10 минут и попробовать снова\n"
        "3️⃣ Отправить ссылку в формате: https://youtu.be/ID_видео\n\n"
        "Если проблема повторяется — напиши мне, я помогу!",
        message.chat.id, msg.message_id
    )

bot.polling()
