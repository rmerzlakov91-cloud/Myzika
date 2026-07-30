import telebot
import requests
import json
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # Получи у @BotFather

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-скачивалка!\n\n"
        "Отправь мне ссылку на видео, и я найду способ его скачать!"
    )

@bot.message_handler(func=lambda m: True)
def get_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на видео.")
        return
    
    msg = bot.reply_to(message, "⏳ Ищу ссылку для скачивания...")
    
    # === СПОСОБ 1: Y2mate API (основной) ===
    try:
        # Получаем ID видео из ссылки
        video_id = None
        id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
        if id_match:
            video_id = id_match.group(1)
        else:
            id_match = re.search(r'youtu\.be/([0-9A-Za-z_-]{11})', url)
            if id_match:
                video_id = id_match.group(1)
        
        if video_id:
            y2mate_api_url = "https://www.y2mate.com/mates/analyzeV2/ajax"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
            }
            data = {
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'vt': 'mp4',
                'type': 'youtube'
            }
            
            response = requests.post(y2mate_api_url, data=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'links' in result['result']:
                    links = result['result']['links']
                    best_link = None
                    # Ищем ссылку с лучшим качеством
                    best_quality = 0
                    for quality, info in links.items():
                        if 'url' in info and info['url']:
                            # Пробуем определить качество
                            q = 0
                            if 'q' in info:
                                try:
                                    q = int(info['q'].replace('p', ''))
                                except:
                                    q = 0
                            if q > best_quality:
                                best_quality = q
                                best_link = info['url']
                    
                    if not best_link:
                        # Если не нашли по качеству, берём первую ссылку
                        for quality, info in links.items():
                            if 'url' in info and info['url']:
                                best_link = info['url']
                                break
                    
                    if best_link:
                        bot.edit_message_text(
                            f"✅ Нашёл ссылку для скачивания!\n\n"
                            f"🔗 {best_link}\n\n"
                            "📌 Открой ссылку в браузере, чтобы сохранить видео!",
                            message.chat.id, msg.message_id
                        )
                        return
    except Exception as e:
        print(f"Y2mate error: {e}")
    
    # === СПОСОБ 2: Ссылка на сайт-помощник (если ничего не работает) ===
    try:
        bot.edit_message_text(
            "🔍 Не удалось найти прямую ссылку.\n\n"
            "Но ты можешь скачать видео здесь:\n"
            "👉 https://savefrom.net/ru/\n\n"
            "Просто вставь туда ссылку на YouTube!",
            message.chat.id, msg.message_id
        )
    except Exception as e:
        bot.edit_message_text(
            "❌ Не удалось найти ссылку.\n\n"
            "Попробуй:\n"
            "1️⃣ Другую ссылку\n"
            "2️⃣ Подождать 2-3 минуты\n"
            "3️⃣ Скачать вручную на savefrom.net",
            message.chat.id, msg.message_id
        )

bot.polling()
