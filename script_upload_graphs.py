
import datetime
import asyncio
import os
from aiogram import Bot
from aiogram.types import FSInputFile
from setting import config
from sys import argv
import Make_graphs
from DB_connection import make_connection
from verify_breaks import get_breaks,get_ans
conn,cur = make_connection()
ans = get_ans(get_breaks(cur))
args = argv

my_id = 872965519

if len(args)>1:
    my_id=args[1]
settings = config()

group_id =872965519
# Константы id бота и канала
API_TOKEN = settings.api_token_bot
CHANNEL_ID = settings.group_id  # это должен быть int, например -1006666666666
bot = Bot(token=API_TOKEN)


# Переменная сегодняшней даты для формирования новой таблицы
now_date = datetime.date.today()
now_date_tag = datetime.date.today().strftime("%y_%m_%d")

async def send_message(name_of_file:str,channel_id: int,flag1:int=1,flag:int=1):
    if os.path.exists(fr"{os.getcwd()}/Reports/{now_date}/Графики_по_тестам_{now_date}.pdf") and flag1>0:
        if flag:
            if ans:
                await bot.send_message(channel_id,f'''{ans}''')
            doc = FSInputFile(path=rf'{name_of_file}_{now_date}.pdf')
            await bot.send_message(channel_id,f'#Отчет_за_{now_date_tag}')
            await bot.send_document(channel_id, document=doc)
        else:
            doc = FSInputFile(path=rf'{name_of_file}_{now_date}.pdf')
            await bot.send_document(channel_id, document=doc)
    else:
        if not bool(ans):
            await bot.send_message(channel_id,f'''#Отчет_за_{now_date_tag}\nРобот не работал до нынешнего момента''')
        else:
            await bot.send_message(channel_id,f'''#Отчет_за_{now_date_tag}\nРобот не работал до нынешнего момента\n{ans}''')

async def sending(name_of_file:str,chat_id,flag1:int=1,flag:int=1):
    await send_message(name_of_file,chat_id,flag1,flag)


async def main(flag:bool=True,chat_id:int=my_id):
    if flag:
        task1 = asyncio.create_task(sending(fr"{os.getcwd()}/Reports/{now_date}/Графики_по_тестам",chat_id))
        task2 = asyncio.create_task(sending(fr"{os.getcwd()}/Reports/{now_date}/Сводка",chat_id,flag1=1,flag=0))

        await task1
        await task2
    else:
        task1 = asyncio.create_task(sending('pupa',chat_id,flag1=0))
        await task1

if __name__ == '__main__':
    Make_graphs.make_folder(True)
    Make_graphs.make_folder()
    count_of_data=Make_graphs.Save_PDF_images_grabs()
    Make_graphs.Save_PDF_images_grabs_gisto()
    if count_of_data:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
    else:
        try:
            asyncio.run(main(False))

        except Exception as e:
            print(e)
