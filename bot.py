import telebot
import time

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"
bot = telebot.TeleBot(TOKEN)

# ID твоей группы
GROUP_ID = -1004459421239

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "✅ Бот активирован!\n\n"
        "Сейчас я напишу /start@TopSaverBot в чате,\n"
        "чтобы активировать бота-помощника."
    )
    
    # Отправляем команду /start в группу
    bot.send_message(GROUP_ID, "/start@TopSaverBot")
    time.sleep(2)
    
    bot.reply_to(message, 
        "✅ Команда отправлена!\n\n"
        "Теперь ты можешь кидать ссылки в чат,\n"
        "и TopSaverBot будет работать."
    )

bot.polling()
