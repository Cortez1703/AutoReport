from sys import platform
from os import path
import os
import datetime

now_date = datetime.date.today()


def make_folder(level: bool = False):
    '''
        Функция создавания папки с названием текущей даты для отчета на сегодняший день.
    Флаг level используется для создания Reports - папки, где хранятся все отчеты
    '''
    if level:
        if platform == "linux" or platform == "linux2":
            if not os.path.exists('Reports'):
                os.mkdir("Reports")
        elif platform == "win32":
            if not os.path.exists(path.abspath('') + fr'\Reports'):
                os.mkdir(path.abspath('') + fr'\Reports')
        else:
            print('pizdec')
    else:
        if platform == "linux" or platform == "linux2":
            if not os.path.exists(fr'Reports/{now_date}') and os.path.exists('Reports'):
                os.mkdir(fr'Reports/{now_date}')
        elif platform == "win32":
            if not os.path.exists(path.abspath('') + fr'\Reports\{now_date}'):
                os.mkdir(path.abspath('') + fr'\Reports\{now_date}')
        else:
            print('pizdec')


make_folder()