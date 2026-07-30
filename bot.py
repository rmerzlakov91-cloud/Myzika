import telebot
import time
import re

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"
bot = telebot.TeleBot(TOKEN)

# ТВОЙ ID ГРУППЫ
GROUP_ID = -1004459421239

# Храним состояния пользователей
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎬 Привет! Я бот-посредник!\n\n"
        "Просто отправь мне ссылку на YouTube,\n"
        "а я скачаю видео в 1080p."
    )

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка! Отправь ссылку на YouTube.")
        return
    
    user_id = message.chat.id
    user_states[user_id] = {'step': 'waiting', 'url': url}
    
    msg = bot.reply_to(message, "⏳ Отправляю ссылку в бот-помощник...")
    
    try:
        # ШАГ 1: Активируем TopSaverBot командой /start
        bot.send_message(GROUP_ID, "/start@TopSaverBot")
        bot.edit_message_text("⏳ Активирую бота-помощника...", message.chat.id, msg.message_id)
        time.sleep(3)  # Даём время на активацию
        
        # ШАГ 2: Отправляем ссылку
        bot.send_message(GROUP_ID, url)
        bot.edit_message_text("⏳ Отправил ссылку, жду ответ...", message.chat.id, msg.message_id)
        time.sleep(5)
        
        # ШАГ 3: Ждём кнопку 1080p
        bot.edit_message_text("⏳ Выбираю качество 1080p...", message.chat.id, msg.message_id)
        time.sleep(3)
        
        # ШАГ 4: Ждём видео
        bot.edit_message_text(
            "⏳ Видео обрабатывается...\n"
            "Подожди 20-40 секунд.",
            message.chat.id, msg.message_id
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка: {str(e)[:150]}\n\n"
            "Попробуй ещё раз.",
            message.chat.id, msg.message_id
        )

# Перехватываем сообщения от TopSaverBot в группе
@bot.message_handler(func=lambda m: m.from_user.username == "TopSaverBot" and m.chat.id == GROUP_ID)
def handle_top_saver_response(message):
    # Если пришло видео — пересылаем пользователю
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
