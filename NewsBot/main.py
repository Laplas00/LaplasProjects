import logging

from aiogram import Bot, Dispatcher, executor, types

from newsapi import NewsApiClient



# from news import *

API_TOKEN = '5929468172:AAEabYLFdXGoGI4PQtB4XdusQcvL2QrzgR4'
NEWS_API = NewsApiClient(api_key='13d433eeebef4040bbc77a9bfa91f6a2')



# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    commands = '/my_id - return the user information\n/sources - return sources for the news\n/find NameOfNews - find nws by topic\n/all'
    await message.reply(f"Hi!\nI'm NewsBot!\nPowered by aiogram. \nMy commans:\n{commands}")


@dp.message_handler(commands=['my_id'])
async def news_handler(message: types.Message):
    await message.reply(message)




@dp.message_handler(commands=['sources'])
async def send_source(message: types.Message):
    '''
        Return the news sources 
    '''
    answer = []
    news_sources = NEWS_API.get_sources()
    print(news_sources)
    for source in news_sources['sources']:
        answer.append(source['name'])
    all_answers = '\n'.join(answer)
    await message.reply(f"Hello, this is sources:\n{all_answers}")


# @inp_err
@dp.message_handler(commands=['find'])
async def find_news(message: types.Message):
    print(message,'MESSAGE')
    args = message["text"].split()
    # new_args = ' '.join(args[1:])
    # print(new_args)
    print(args)
    answer = []
    top_headlines = NEWS_API.get_top_headlines(
        q=args[1],
        language='en',
    )
    print(top_headlines['articles'])
    for article in top_headlines['articles']:
        answer.append(f"Title : {article['title']}")
        answer.append(f"Description : {article['description']} \n\n")
    result = '\n'.join(answer)
    
    await message.answer(result)
    

# @inp_err
@dp.message_handler(commands=['all'])
async def all_news(message: types.Message):
    print(message,'MESSAGE')
    args = message["text"].split()
    new_args = ' '.join(args[1:])
    print(new_args)
    print(args)
    answer = []
    all_articles = NEWS_API.get_everything(
        q=new_args,
        language='en',   
    )
    for article in all_articles['articles']:
        answer.append(f"Source : {article['source']['name']}")
        answer.append(f"Title : article['title']")
        answer.append(f"Description : {article['description']}\n\n")
    result = '\n'.join(answer)
    await message.reply(result)
    


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, timeout=5, on_shutdown='reload')




# @dp.message_handler()
# async def echo(message: types.Message):
#     # old style:
#     # await bot.send_message(message.chat.id, message.text)
#     logging.info(f"Received arguments: arg1={message}")
#     await message.answer(message.text)