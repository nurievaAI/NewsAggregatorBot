import typing as tp
import aiohttp
import os
import googlesearch
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


proxy_host = os.environ.get('PROXY', None)
proxy_credentials = os.environ.get('PROXY_CREDS', None)
if proxy_credentials:
    login, password = proxy_credentials.split(':')
    proxy_auth: tp.Any = aiohttp.BasicAuth(login=login, password=password)
else:
    proxy_auth = None

bot = Bot(token=os.environ['BOT_TOKEN'],
          proxy=proxy_host, proxy_auth=proxy_auth)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message) -> None:
    await message.reply(
                        'Добрый день! Вас приветствует Бот, я помогу Вам получать подборку персонализированных новостей, которые Вам интресны. \n' +
                        'Введите через запятую теги, по которым хотите подборку.'
                        )


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await message.reply(
                        'Введите /start, вернуться в начало. \n' +
                        'Напишите @parrampaparam, если возникнут проблемы с ботом.'
                        )

@dp.message_handler()
async def process_query(message: types.Message) -> None:
    tags = message.text.split(',')
    for i in range(len(tags)):
        tags[i] = tags[i].lstrip()
    print(tags)
    params = {
        'api_key': '635dde2d2bb842ccbfbf3a977a8598ef',
        'query': tags
    }
    for i in range(len(tags)):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://newsapi.org/v2/everything?q=' + params['query'][i] + '&apiKey=' + params['api_key'], params={'sortBy': 'publishedAt'}) as response:
                data = await response.json()

        print(data)

        if (data['status'] != 'ok'):
            caption_error =\
                'ERROR!!!\n' +\
                'TAG :  ' + tags[i] + '\n' +\
                'STATUS :  ' + data['status'] + '\n' +\
                'ERROR CODE :  ' + data['code'] + '\n' +\
                'ERROR MESSAGE :  ' + data['message'] + '\n' 
            await bot.send_message(message.chat.id, caption_error)
            continue

        n = min(3, data['totalResults'])

        if (data['totalResults'] == 0):
            await bot.send_message(message.chat.id, 'К сожалению, по тегу #{} ничего не найдено.'.format(tags[i].replace(' ', '')))
        for j in range(n):
            entry = data['articles'][j]
            title = entry['title'] if entry.get('title') else '*no title*'
            published_date = entry['publishedAt'][0:10] if entry.get('publishedAt') else '*no pudlished date*'
            content = entry['content'] if entry.get('content') else '*no overview*'
            link = entry['url'] if entry.get('url') else '*no url*'

            caption =\
                'TAG #' + tags[i].replace(' ', '') + '\n' +\
                'TITLE: ' + title + '\n' +\
                'PUBLISHED: ' + published_date + '\n' +\
                'LINK: \n' + link
            await bot.send_message(message.chat.id, caption)

if __name__ == '__main__':
    executor.start_polling(dp)
