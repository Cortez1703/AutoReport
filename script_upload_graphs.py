#Aiogram imports
from aiogram import Bot
from aiogram.types import FSInputFile
#Local imports
from DB_connection import make_connection
from Creater_image import Creater_image
from Executer import Executer as Ex
from verify_breaks import get_ans,get_breaks
from Make_folder import make_folder
#Standart imports
import datetime
import asyncio
import os
from sys import argv
import yaml



Executer = Ex()
conn,cur = make_connection()
Creater_im = Creater_image(cur,conn,Executer)

args = argv
ans = get_ans(get_breaks(cur))
my_id = -1002259594246 
message_id=''

if len(args)>1:
    my_id=int(args[1])
    message_id = int(args[2])

with open('config.yaml') as f:
            dataframe = yaml.load(f,yaml.FullLoader)

group_id =872965519
# Константы id бота и канала
API_TOKEN = dataframe['api_token_bot']
CHANNEL_ID = group_id  # это должен быть int, например -1006666666666
bot = Bot(token=API_TOKEN)


# Переменная сегодняшней даты для формирования новой таблицы
now_date = datetime.date.today()
now_date_tag = datetime.date.today().strftime("%y_%m_%d")

async def send_message(name_of_file:str,channel_id: int,flag1:int=1,flag:int=1):
    if os.path.exists(fr"./Reports/{now_date}/Графики_по_тестам_{now_date}.pdf") and flag1>0:
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
            if message_id:
                await bot.delete_message(channel_id,message_id-1)
        else:
            await bot.send_message(channel_id,f'''#Отчет_за_{now_date_tag}\nРобот не работал до нынешнего момента\n{ans}''')
            if message_id:
                await bot.delete_message(channel_id,message_id-1)

async def sending(name_of_file:str,chat_id,flag1:int=1,flag:int=1):
    await send_message(name_of_file,chat_id,flag1,flag)


async def main(flag:bool=True,chat_id:int=my_id):
    if flag:
        task1 = asyncio.create_task(sending(fr"./Reports/{now_date}/Графики_по_тестам",chat_id))
        task2 = asyncio.create_task(sending(fr"./Reports/{now_date}/Сводка",chat_id,flag1=1,flag=0))

        await task1
        await task2
    else:
        task1 = asyncio.create_task(sending('pupa',chat_id,flag1=0))
        await task1

if __name__ == '__main__':
    make_folder(True)
    make_folder()
    flag = Creater_im.Save_PDF_images_grabs()
    #Creater_im.Save_PDF_images_grabs_gisto()
    if flag:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
    else:
        try:
            asyncio.run(main(False))
        except Exception as e:
            print(e)
