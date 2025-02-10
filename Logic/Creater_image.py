# Matplotlib/NumPy imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *

# Local imports
from Logic.Creater_right_data import Creater
from statistics import mean
from Logic.Executer import Executer
from Logic.DB_connection import make_connection


# Standart imports
import datetime
import os
import yaml
import time
# const

connection, cursor = make_connection()


class Creater_image(Creater):

    """
        Конструктор для создания и сохранения графиков в пдф
    """

    def __init__(self, cur, con, Executer, deltaDays):
        super().__init__(cur, con,deltaDays)
        self.now_date = datetime.date.today()-datetime.timedelta(days=deltaDays)
        self.Executer = Executer(cur, con)
        self.deltaDays = deltaDays
        self.pdf = PdfPages(
            fr"{os.getcwd()}/Reports/{self.now_date}/Графики_по_тестам_{self.now_date}.pdf")
        self.pdf2 = PdfPages(
            fr"{os.getcwd()}/Reports/{self.now_date}/Сводка_{self.now_date}.pdf")

    def _make_graph(self, x_label: list, x_label_2, y_label: list, y_label_2: list, title: str):
        """
        Функция, используемая для создания общего графика работы за раб.день
        """
    # Какой-то костыль, без которого не будет работать
        fmt = dates.DateFormatter('%H:%M:%S')

        # Экземпляры фигуры и графика
        fig, ax = plt.subplots()

        # Отрисовка самих графиков
        ax.plot(x_label, y_label, '-.', color='b',
                label='Попыток захвата', markersize=1)
        ax.plot(x_label_2, y_label_2, "--", color='r', label='Успешный захват')

        ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                         успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (len(y_label+1))) * 100:.2f}%''')

        ax.title.set_fontsize(10)
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(fmt)
        if len(x_label) > 0 and len(x_label_2) > 0:
            ax.set_xlim(x_label[0],
                        max(x_label[-1], x_label_2[-1]))

        fig.autofmt_xdate()

        return fig

    def _Save_PDF_bar(self, ax: plt.axes):
        fmt = dates.DateFormatter('%H:%M:%S')
        """
        Функция для создания общего графика по категориям за день
        """
        # Словари для столбчатого графика.
        grab_bar, sorted_bar = self.Executer.axis_bar_graph(
            self.now_date_start, self.now_date_end)

        # Сортировка по возравстанию ключей(чтоб сопоставить с подписями)
        grab_bar = dict(sorted(grab_bar.items()))
        sorted_bar = dict(sorted(sorted_bar.items()))

        # Инициализация конструктора
        # fig = plt.figure(figsize=(25, 20))
        # ax = fig.add_subplot(2, 1, 2)

        # Добавление подписей графиков (категорий)
        with open('config.yaml') as f:
            dataframe = yaml.load(f, yaml.FullLoader)

        for category in grab_bar.keys():
            grab_bar[category].append(
                dataframe['dataframes'][str(category)][6:])

        # Списки для самих столбчатых графиков
        list_for_graphs_y1 = [i[0] for i in grab_bar.values()]
        list_for_graphs_y2 = [i[0] for i in sorted_bar.values()]

        # Ось Х
        x_level = np.arange(len(list_for_graphs_y1))

        # Массив КПД по столбцам (для наглядности)
        list_of_KPD = [
            f'{round((sorted[0]/grab[0])*100, 2)}%' for grab, sorted in zip(grab_bar.values(), sorted_bar.values())]

        # Массив категорий. Для подписи около каждого столбца
        category_names = [i[1] for i in grab_bar.values()]

        # Добавление графиков. Первый проинициализирован, т.к. далее берется его высота, чтобы значение КПД отображалось над ним
        grabs = ax.bar(x_level, list_for_graphs_y1, width=0.5, linewidth=2,
                       yerr=2, label='Количество попыток захвата')
        ax.bar(x_level, list_for_graphs_y2, width=0.5, linewidth=2,
               yerr=2, label='Количество успешных захватов')

        # Конструктор отображения КПД
        for grab, text in zip(grabs, list_of_KPD):
            yval = grab.get_height()
            plt.text(grab.get_x() + grab.get_width() / 2,
                     yval+0.5, text, ha='center', va='bottom', fontsize=8)

        # Параметры matplotlib. Legend(loc=0) - позиция легенды. 0 - лучшее
        # set_xticklabels - параметры отображения названий категорий
        ax.legend(loc=0)
        ax.set_xticks(x_level)
        ax.set_xticklabels(category_names, rotation=20, ha='right')
        ax.grid()

    def _Save_PDF_big_graph(self, ax):
        """Конструктор графика за весь день"""
        x_label, y_label = self.get_current_time(
            "grab_attempt", "attempt_timestamp")
        x_label_2, y_label_2 = self.get_current_time(
            "grab_attempt", "attempt_timestamp", success=True)

        title = 'Общая статистика'
        fmt = dates.DateFormatter('%H:%M:%S')

        # Отрисовка самих графиков
        ax.plot(x_label, y_label, '-.', color='g',
                label='Попыток захвата', markersize=1)
        ax.plot(x_label_2, y_label_2, "--", color='r', label='Успешный захват')

        # Добавление данных по поломкам
        data_of_breaks = self.Executer.data_of_breaks(
            self.now_date_start, self.now_date_end)

        text = ''

        for breakData in data_of_breaks:
            if breakData[1]:

                timedelta = breakData[1]-breakData[2]

                text += f'''{breakData[0]}, время ремонта:{timedelta.days*8 + timedelta.seconds//3600}ч,{
                    (timedelta.seconds % 3600)//60}м,{(timedelta.seconds % 3600) % 60}с\n'''
            else:
                text += f'{breakData[0]}, ремонт не закончен\n'

        if text:
            text = f'Поломки за {self.now_date}\n\n'+text
            ax.text(self.now_date_start, y_label[int(len(y_label)*0.8)], f'{text}', style='italic',
                    fontsize=10,
                    bbox={'facecolor': 'green',
                          'alpha': 0.6, 'pad': 2})
        if len(y_label):

            ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                            успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (y_label[-1]+1)) * 100:.2f}%''')

            ax.title.set_fontsize(10)
            ax.legend()
            ax.grid(True)
            ax.xaxis.set_major_formatter(fmt)
            if len(x_label) > 0 and len(x_label_2) > 0:
                ax.set_xlim(min(x_label[0], x_label_2[0]),
                            max(x_label[-1], x_label_2[-1]))

    def _Save_PDF_full_graph(self, flag: int = 0):
        """
        Функция создания массива графиков по запущенным тестам
        """
        test_id = self.Executer.get_test_id(
            self.now_date_start, self.now_date_end)

        # Парсинг данных по разным тестам робота (каждый запуск = новая порция датки)
        for idshnik in sorted(test_id):
            x_label, y_label = self.get_current_time(
                "grab_attempt", "attempt_timestamp", idshnik)
            x_label_2, y_label_2 = self.get_current_time(
                "grab_attempt", "attempt_timestamp", idshnik, True)
            if len(x_label) > 0 or len(x_label_2) > 0:
                flag += 1

            title = f'Статистика для опыта №{idshnik}'

            self.pdf.savefig(self._make_graph(
                x_label, x_label_2, y_label, y_label_2, title))

            time.sleep(0.1)

        # Создание и сохранение общего графика + столбчатого по категориям
        if flag:
            fig = plt.figure(figsize=(25, 20))
            # Общий график за день
            ax = fig.add_subplot(2, 1, 1)
            self._Save_PDF_big_graph(ax)

            # Столбчатый график
            ax = fig.add_subplot(2, 1, 2)
            self._Save_PDF_bar(ax)

            self.pdf.savefig(fig)
            # Сохранение общего графика за сегодняшнюю дату

            self.pdf.close()
            return bool(flag)
        else:
            return None

    def _Save_PDF_speed_graph(self, time_step: int = 1):
        plt.close('all')
        x_full = []
        x_succec = []
        y_full = []
        y_succel = []

        # Сохранение общего графика за сегодняшнюю дату

        full_worktime, _ = self.get_current_time(
            "grab_attempt", "attempt_timestamp")
        second_worktime, _ = self.get_current_time(
            "grab_attempt", "attempt_timestamp", success=True)
        # Не советую даже разбираться в этом.Должно работать. Если коротко - создает график скорости захватов(в минуту) от времени
        for hour in np.arange(9, 20):
            y_full_sum = 0
            y_succes_sum = 0
            for minute in range(0, 60, time_step):
                Counter_grab = 0
                Counter_success = 0
                start = datetime.datetime.combine(datetime.datetime.now(
                ).date()-datetime.timedelta(self.deltaDays), datetime.time(hour, minute, 0))

                x_full.append((hour+(minute/60)))
                x_succec.append(hour+(minute/60))
                y_succes_sum = 0
                y_full_sum = 0
                work_list = full_worktime[Counter_grab::]
                for elem_time in work_list:

                    if minute == 59:
                        end = datetime.datetime.combine(datetime.datetime.now().date(
                        )-datetime.timedelta(self.deltaDays), datetime.time(hour, minute, 59))
                        if elem_time > start and elem_time < end:
                            Counter_grab += 1

                            y_full_sum += 1
                    else:
                        end = datetime.datetime.combine(datetime.datetime.now().date(
                        )-datetime.timedelta(self.deltaDays), datetime.time(hour, minute+time_step, 0))
                        if elem_time > start and elem_time < end:
                            Counter_grab += 1
                            y_full_sum += 1

                for elem_time in second_worktime[Counter_success::]:

                    if minute == 59:
                        end = datetime.datetime.combine(datetime.datetime.now().date(
                        )-datetime.timedelta(self.deltaDays), datetime.time(hour, minute, 59))
                        if elem_time > start and elem_time < end:
                            Counter_success += 1
                            y_succes_sum += 1
                    else:
                        end = datetime.datetime.combine(datetime.datetime.now().date(
                        )-datetime.timedelta(self.deltaDays), datetime.time(hour, minute+time_step, 0))
                        if elem_time > start and elem_time < end:
                            Counter_success += 1
                            y_succes_sum += 1

                y_full.append(y_full_sum)
                y_succel.append(y_succes_sum)
        plt.rcParams["figure.figsize"] = (25, 15)
        plt.step(x_full, y_full, label='Общее количество попыток')
        plt.step(x_succec, y_succel, label='Количество успешных попыток')

        wave_grab_median_y = []
        wave_success_median_y = []

        for counter in range(len(y_full)):
            wave_list = y_full[counter:counter+20]
            wave_grab_median_y.append(sum(wave_list)/len(wave_list))
        for counter in range(len(y_succel)):
            wave_list = y_succel[counter:counter+20]
            wave_success_median_y.append(sum(wave_list)/len(wave_list))
        plt.plot(x_full, wave_grab_median_y, color='black')
        plt.plot(x_succec, wave_success_median_y, color='red')
        while 0 in y_succel:
            y_succel.remove(0)

        plt.legend()
        plt.title(f"""Общее количество попыток {sum(y_full)}, количество успешных попыток {sum(y_succel)}.
    КПД {(sum(y_succel) / (1+sum(y_full))) * 100:.2f}%""")
        plt.grid(True)
        plt.xlabel("Время в часах")
        plt.ylabel("V,предметы/минута")
        if y_full:

            plt.xlim(min(x_succec[0], x_full[0]),
                     max(x_full[-1], x_succec[-1]))
            plt.ylim(0, max(y_full)+10)
            self.pdf2.savefig()

    def _Save_PDF_images_odometr_gisto(self):
        x_label = [0 for i in range(6)]
        y_label = [0 for i in range(14)]
        z_label = [0 for i in range(6)]
        x_area = ["-0.3:-0.2", "-0.2:-0.1",
                  '-0.1:0', "0:0.1", "0.1:0.2", "0.2:0.3"]
        y_area = ['5:6', '0.6:0.7', '0.7:0.8', '0.8:0.9', '0.9:1', '1:1.1', '1.1:1.2',
                  '1.2:1.3', '1.3:1.4', '1.4:1.5', '1.5:1.6', '1.6:1.7', '1.7:1.8', '1.8:2']
        z_area = ["-0.500:-0.475", "-0.475:-0.450",
                  '-0.450:-0.425', "-0.425:-0.400", "-0.400:-0.375", "-0.375:-0.300"]
        d = 0
        Test_id = self.Executer.get_test_id(
            self.now_date_start, self.now_date_end)
        for test_id in Test_id:
            x_distribution = self.make_right_odometr(
                self.Executer.get_data_odometr(test_id, "x_distribution"))
            y_distribution = self.make_right_odometr(
                self.Executer.get_data_odometr(test_id, "y_distribution"))
            z_distribution = self.make_right_odometr(
                self.Executer.get_data_odometr(test_id, "z_distribution"))
            distance = self.make_right_odometr(
                self.Executer.get_data_odometr(test_id, "distance"))
            if x_distribution and y_distribution and z_distribution and distance:
                x_label = [x+y for x, y, in zip(x_label, x_distribution)]
                y_label = [x+y for x, y, in zip(y_label, y_distribution)]
                z_label = [x+y for x, y, in zip(z_label, z_distribution)]
                d += distance

        x_level = np.arange(len(x_area))
        y_level = np.arange(len(y_area))
        z_level = np.arange(len(z_area))
        fig = plt.figure(figsize=(25, 25))
        fig.suptitle(f"""Распределение нахождения робота по областям. Общее время работы - {
                     sum((x_label)):.2f} мин. \n Пройденная дистанция - {d} м""")
        ax = fig.add_subplot(1, 3, 1)
        ax.grid(True)
        ax.bar(x_level, x_label)
        ax.set_xticks(x_level)
        ax.set_xticklabels(x_area, rotation=20, ha="center")
        ax.set_title("Распределение времени нахождения в областях по X")
        ax = fig.add_subplot(1, 3, 2)
        ax.grid(True)
        ax.bar(y_level, y_label)
        ax.set_xticks(y_level)
        ax.set_xticklabels(y_area, rotation=45, ha="center")
        ax.set_title("Распределение времени нахождения в областях по Y")
        ax = fig.add_subplot(1, 3, 3)
        ax.grid(True)
        ax.bar(z_level, z_label)
        ax.set_xticks(z_level)
        ax.set_xticklabels(z_area, rotation=20, ha="center")
        ax.set_title("Распределение времени нахождения в областях по Z")

        self.pdf2.savefig()
        self.pdf2.close()

    def Save_Full(self):
        result = self._Save_PDF_full_graph()
        if result:
            self._Save_PDF_speed_graph()
            self._Save_PDF_images_odometr_gisto()
            return result
        else:
            return None
