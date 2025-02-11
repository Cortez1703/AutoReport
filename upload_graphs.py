# Aiogram imports
from aiogram import Bot
from aiogram.types import FSInputFile
# Local imports
from Logic.DB_connection import make_connection
from Logic.verify_breaks import get_ans, get_breaks
# Standart imports
import datetime
import asyncio
import os
from sys import argv
import yaml


conn, cur = make_connection()

args = argv
ans = get_ans(get_breaks(cur))

message_id = ''

with open('config.yaml') as f:
    dataframe = yaml.load(f, yaml.FullLoader)

# Константы id бота и канала
bot = Bot(token=dataframe['api_token_bot'])
output_chat_id = dataframe['group_id']

if len(args) > 1:
    output_chat_id = int(args[1])
    message_id = int(args[2])


# Переменная сегодняшней даты для формирования новой таблицы
now_date = datetime.date.today()
now_date_tag = datetime.date.today().strftime("%y_%m_%d")

args = argv
ans = get_ans(get_breaks(cur))


deltaDays = 0



async def send_message(channel_id: int):
    if os.path.exists(f"./Reports/{now_date}"):
        if bool(os.listdir(f'./Reports/{now_date}')):
            doc1 = FSInputFile(
                path=rf'./Reports/{now_date}/Графики_по_тестам_{now_date}.pdf')
            doc2 = FSInputFile(
                path=rf'./Reports/{now_date}/Сводка_{now_date}.pdf')
            await bot.send_message(channel_id, f'#Отчет_за_{now_date_tag}')
            await bot.send_document(channel_id, document=doc1)
            await bot.send_document(channel_id, document=doc2)

    else:

        await bot.send_message(channel_id, f'''#Отчет_за_{now_date_tag}\nРобот не работал до нынешнего момента\n{ans}''')


async def main():
    task1 = asyncio.create_task(send_message(output_chat_id))
    await task1


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
