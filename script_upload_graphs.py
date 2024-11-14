import datetime
import asyncio
import os

from aiogram import Bot
from aiogram.types import FSInputFile
from sys import argv

import Make_graphs

from DB_connection import make_connection
from verify_breaks import get_breaks,get_ans

conn,cur = make_connection()

ans = get_ans(get_breaks(cur))

args = argv
print(args)

my_id = 872965519
message_id=''

if len(args)>1:
    my_id=int(args[1])
    message_id = int(args[2])

class config():
    def __init__(self):
        self.DB_CONFIG={
    'dbname': 'ram_testing',
    'user': 'ram',
    'password': 'fuckingdatabase',
    'host': '192.168.6.157',
    'port': 5440
}
        self.id_my=872965519
        self.group_id=-1002259594246
        self.api_token_bot='7725614078:AAFv71izXkxQ5LKoB28Etrf7rMteYo0dw_I'
        self.dataframes = {
    "1": "1.1.1_Бутылки-Прозрачный",
    "2": "1.1.2_Бутылка-Светло-Зелёный",
    "3": "1.1.3_Бутылка-Голубой",
    "4": "1.1.4_Бутылка-Тёмно-Зелёный",
    "5": "1.1.5_Бутылка-Коричневый",
    "6": "1.1.6_Бутылка-Чёрный",
    "7": "1.1.7_Бутылка-Белый",
    "8": "1.1.8_Бутылка-От-Масла",
    "9": "1.1.9_Бутылка-Нестандарт",
    "10": "1.1.10_Бутылка-Этикетка-С-Термоусадкой",
    "11": "1.2.1_Крышки-От-Бутылок",
    "12": "1.2.2_Флаконы-От-Косметики-И-Химии-Белые",
    "13": "1.2.3_Флаконы-От-Косметики-И-Химии-Цветные",
    "14": "1.2.4_Канистры-От-Бензина",
    "15": "1.2.5_Канистры-От-Масла",
    "16": "1.2.6_Товары-Для-Дома-Лейки-Горшки-Контейнеры",
    "17": "1.2.7_ПНД-Ведро",
    "18": "1.2.8_ПНД-Ящик",
    "19": "1.3.1_Прозрачная-Плёнка-И-Пакеты",
    "20": "1.3.2_Белые-Пакеты-Для-Продуктов-От-Молока-От-Порошка",
    "21": "1.3.3_Цветные-Пакеты",
    "22": "1.3.4_Чёрные_Пакеты",
    "23": "1.3.5_Шуршащие-Прозрачные-Пакеты",
    "24": "1.3.6_Шуршащие-Белые-Пакеты",
    "25": "1.3.7_Шуршащие-Цветные-Пакеты",
    "26": "1.4.1_Одноразовая-Посуда-Полипропилен",
    "27": "1.5.1_Подложки-Под-Продукты-И-Яйца-Полистирол",
    "28": "1.6.1_Пластик-Другой",
    "29": "1.6.2_Плёнки-Другие",
    "30": "2.1.1_Гофрокартон-Упаковочные-Коробки",
    "31": "2.1.2_Однослойный-Картон-Втулки-От-ТуалетБумаги-Открытки-Визитки",
    "32": "2.2.1_Газетная-Бумага-Газеты-Книги-Тетради",
    "33": "2.2.2_Глянцевая-Бумага-Журналы-Буклеты-Календари",
    "34": "2.2.3_Офисная-Бумага-Конверты",
    "35": "2.3.1_Макулатура-Другая",
    "36": "3.1.1_Алюминиевые-Банки",
    "37": "3.1.2_Алюминиевые-Балончики",
    "38": "3.2.1_Жестяные-Консервные-Банки-Банки-От-Чая",
    "39": "3.2.2_Жестяные-Крышки-От-Стеклянных-Банок",
    "40": "3.3.1_Металлолом",
    "41": "3.4.1_Фольга",
    "42": "3.5.1_Металлические-Изделия-Другие",
    "43": "4.1.1_Стеклянные-Банки-И-Бутылки-Прозрачные",
    "44": "4.1.2_Стеклянные-Бутылки-Зелёные",
    "45": "4.1.3_Стеклянные-Бутылки-Коричневые",
    "46": "4.1.4_Стеклянные-Изделия-Другие",
    "47": "5.1.1_Tetra Pak",
    "48": "6.1.1_Текстиль",
    "49": "7.1.1_Органические-Отходы",
    "50": "8.1.1_Опасные-Отходы",
    "51": "9.1.1_Дерево-И-Доски",
    "52": "10.1.1_Шины-И-Покрышки",
    "53": "11.1.1_Электроприборы",
    "54": "12.1.1_Вторсырьё-Другое"}

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
    Make_graphs.make_folder(True)
    Make_graphs.make_folder()
    print(1)
    count_of_data=Make_graphs.Save_PDF_images_grabs()
    Make_graphs.Save_PDF_images_grabs_gisto()
    print(count_of_data)
    if count_of_data:
        try:
            print(1)
            asyncio.run(main())
        except Exception as e:
            print(e)
    else:
        try:
            asyncio.run(main(False))

        except Exception as e:
            print(e)
