import telebot
import requests
import json
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"  # ВСТАВЬ СВОЙ ТОКЕН

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
    
    # === СПОСОБ 1: SaveFrom API (самый быстрый) ===
    try:
        api_url = "https://api.savefrom.net/2/"
        params = {
            'url': url,
            'ajax': 1,
            'lang': 'ru'
        }
        
        response = requests.get(api_url, params=params, timeout=15)
        data = response.json()
        
        if 'result' in data and 'files' in data['result']:
            files = data['result']['files']
            
            # Ищем лучшую ссылку
            best_link = None
            best_quality = 0
            
            for quality, info in files.items():
                if 'link' in info:
                    link = info['link']
                    # Пытаемся определить качество
                    quality_num = 0
                    if 'quality_label' in info:
                        match = re.search(r'(\d+)', info['quality_label'])
                        if match:
                            quality_num = int(match.group(1))
                    elif 'quality' in info:
                        match = re.search(r'(\d+)', str(info['quality']))
                        if match:
                            quality_num = int(match.group(1))
                    
                    if quality_num > best_quality:
                        best_quality = quality_num
                        best_link = link
            
            if best_link:
                bot.edit_message_text(
                    f"✅ Нашёл ссылку для скачивания!\n\n"
                    f"🔗 {best_link}\n\n"
                    "📌 Открой ссылку в браузере, чтобы сохранить видео!",
                    message.chat.id, msg.message_id
                )
                return
    except:
        pass  # Если не сработало — переходим к способу 2
    
    # === СПОСОБ 2: Другой API (запасной) ===
    try:
        # Используем API от y2mate (ещё один сайт-помощник)
        y2mate_api = "https://www.y2mate.com/mates/analyzeV2/ajax"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Парсим ID видео
        video_id = None
        id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
        if id_match:
            video_id = id_match.group(1)
        
        if video_id:
            data = {
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'vt': 'mp4',
                'type': 'youtube'
            }
            
            response = requests.post(y2mate_api, data=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'links' in result['result']:
                    links = result['result']['links']
                    # Берём первую ссылку
                    for quality, info in links.items():
                        if 'url' in info:
                            bot.edit_message_text(
                                f"✅ Нашёл ссылку для скачивания!\n\n"
                                f"🔗 {info['url']}\n\n"
                                "📌 Открой ссылку в браузере, чтобы сохранить видео!",
                                message.chat.id, msg.message_id
                            )
                            return
    except:
        pass  # Если не сработало — переходим к способу 3
    
    # === СПОСОБ 3: Ссылка на сайт-помощник ===
    try:
        # Если ничего не получилось — даём ссылку на SaveFrom
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
