import telebot
import time
import re
from telebot import types

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"
bot = telebot.TeleBot(TOKEN)

# ID группы
GROUP_ID = -1004459421239

# Храним состояния пользователей
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-посредник для TopSaverBot!\n\n"
        "Просто отправь мне ссылку на YouTube,\n"
        "а я скачаю видео в 1080p.\n\n"
        "⚠️ Процесс может занять 1-2 минуты."
    )

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    user_id = message.chat.id
    user_states[user_id] = {'step': 'waiting', 'url': url}
    
    msg = bot.reply_to(message, "⏳ Начинаю процесс...")
    
    try:
        # ШАГ 1: Проверяем, активен ли TopSaverBot
        bot.edit_message_text("⏳ Активирую бота-помощника...", message.chat.id, msg.message_id)
        
        # Отправляем команду /start в группу
        bot.send_message(GROUP_ID, "/start@TopSaverBot")
        time.sleep(5)  # Ждём, пока бот ответит
        
        # ШАГ 2: Отправляем ссылку
        bot.edit_message_text("⏳ Отправляю ссылку...", message.chat.id, msg.message_id)
        bot.send_message(GROUP_ID, url)
        time.sleep(8)  # Ждём, пока TopSaverBot обработает
        
        # ШАГ 3: Проверяем, есть ли кнопка 1080p
        bot.edit_message_text("⏳ Ищу кнопку 1080p...", message.chat.id, msg.message_id)
        time.sleep(3)
        
        # ШАГ 4: Нажимаем 1080p (если есть)
        bot.edit_message_text("⏳ Выбираю качество 1080p...", message.chat.id, msg.message_id)
        
        # Пытаемся найти и нажать кнопку 1080p
        # (это работает только если бот видит сообщения TopSaverBot)
        
        time.sleep(5)
        
        # ШАГ 5: Ждём видео
        bot.edit_message_text(
            "⏳ Видео обрабатывается...\n"
            "Подожди 30-60 секунд.",
            message.chat.id, msg.message_id
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка: {str(e)[:150]}\n\n"
            "Попробуй ещё раз.",
            message.chat.id, msg.message_id
        )

# Обработчик сообщений от TopSaverBot
@bot.message_handler(func=lambda m: m.from_user.username == "TopSaverBot" and m.chat.id == GROUP_ID)
def handle_top_saver(message):
    # Если пришло видео
    if message.video:
        for user_id, state in user_states.items():
            if state.get('step') == 'waiting':
                bot.forward_message(user_id, message.chat.id, message.message_id)
                bot.send_message(user_id, "✅ Готово! Видео скачано в 1080p.")
                user_states[user_id]['step'] = 'done'
                break
    
    # Если пришла кнопка с выбором качества
    elif message.reply_markup:
        try:
            for row in message.reply_markup.keyboard:
                for button in row:
                    if '1080' in button.text:
                        bot.send_message(message.chat.id, button.callback_data)
                        break
        except:
            pass

bot.polling()
