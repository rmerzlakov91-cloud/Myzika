import os
import yt_dlp
import asyncio
from aiogram import Bot, Dispatcher, F
import nest_asyncio
from aiogram import html

nest_asyncio.apply()

TOKEN = "8912629367:AAGDvBUBFE97vLTPzlXsbmALJHi0u3XUCjs"

bot = Bot(TOKEN)
dp = Dispatcher()

def get_direct_link(video_url):
    ydl_opts = {
        'format': 'best[height<=360]',  # Скачиваем в 360p (быстро)
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'socket_timeout': 60,  # Даём YouTube 60 секунд на ответ
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
    L = info_dict['formats']
    for x in range(len(L)):
        if L[x].get('height', 0) == 1280:
            direct_link = L[x]['url']
            return direct_link


@dp.message(F.text == '/start')
async def handler(message):
    await message.reply('Просто напиши мне ссылку на видео youtube, а я скачаю его для тебя)')


@dp.message(F.text.regexp(r'^https:\/\/(www\.youtube.*|youtu\.be.*|youtube\.com.*)'))
async def handler(message):
    url = str(message.text)
    await message.reply('⏳ Начинаю скачивание... Подожди немного.')
    try:
        direct_link = get_direct_link(url)
        text = html.link('Вот, лови', html.quote(direct_link))
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.reply(f'❌ Ошибка при скачивании: {str(e)[:150]}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot, skip_updates=True))
    loop.run_forever()
