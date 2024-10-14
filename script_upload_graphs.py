
import datetime
import asyncio
import os
from aiogram import Bot
from aiogram.types import FSInputFile
from setting import config

settings = config()

group_id =1
# Константы id бота и канала
API_TOKEN = settings.api_token_bot
CHANNEL_ID = settings.id_my  # это должен быть int, например -1006666666666
bot = Bot(token=API_TOKEN)

# Переменная сегодняшней даты для формирования новой таблицы
now_date = datetime.date.today()

async def send_message(channel_id: int,name_of_file:str):
    doc = FSInputFile(path=rf'{name_of_file}_{now_date}.pdf')
    await bot.send_document(channel_id, doc)

async def sending(name_of_file:str):
    await send_message(CHANNEL_ID,name_of_file)


async def main():
    task1 = asyncio.create_task(sending(fr"{os.getcwd()}/Reports/{now_date}/Графики_по_тестам"))
    task2 = asyncio.create_task(sending(fr"{os.getcwd()}/Reports/{now_date}/Сводка"))

    await task1
    await task2



asyncio.run(main())

if __name__ == '__main__':
    try:
        asyncio.run(main())

    except Exception as e:
        print(e)

