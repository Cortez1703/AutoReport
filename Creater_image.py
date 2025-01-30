# Matplotlib/NumPy imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *

# Local imports
from Creater_right_data import Creater
from statistics import mean
from Make_folder import make_folder
from Executer import Executer as Ex
from DB_connection import make_connection


# Standart imports
import datetime
import os
import yaml
import time

Executer = Ex()
connection, cursor = make_connection()


class Creater_image(Creater):

    """
        Конструктор для создания и сохранения графиков в пдф
    """

    def __init__(self, cur, con, Exec):
        super().__init__(cur, con, Exec)
        self.now_date = datetime.date.today()
        self.pdf = PdfPages(
            fr"{os.getcwd()}/Reports/{self.now_date}/Графики_по_тестам_{self.now_date}.pdf")
        self.pdf2 = PdfPages(
            fr"{os.getcwd()}/Reports/{self.now_date}/Сводка_{self.now_date}.pdf")

    def make_graph(self, x_label: list, x_label_2, y_label: list, y_label_2: list, title: str):
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
        if len(y_label) < 1:
            ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                         успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (len(y_label+1))) * 100:.2f}%''')
        else:
            ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                         успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (y_label[-1])) * 100:.2f}%''')
        ax.title.set_fontsize(10)
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(fmt)
        if len(x_label) > 0 and len(x_label_2) > 0:
            ax.set_xlim(min(x_label[0], x_label_2[0]),
                        max(x_label[-1], x_label_2[-1]))

        fig.autofmt_xdate()

        return fig

    def Save_PDF_images_gisto(self):
        fmt = dates.DateFormatter('%H:%M:%S')
        """
        Функция для создания общего графика по категориям за день
        """
        dict_grab = {}
        dict_sorted = {}
        list_of_category_grab, list_of_category_sorted = self.Executer.data_of_sorted(
            self.now_date_start, self.now_date_end)
        # Добавление количества включений той или иной категории
        for i in set(list_of_category_grab):
            dict_grab[i] = list_of_category_grab.count(i)
        for i in set(list_of_category_sorted):
            dict_sorted[i] = list_of_category_sorted.count(i)

        # Составление словаря ключ(категория):значение(всего попыток,успешных|0)
        for i, j in dict_grab.items():
            dict_grab[i] = [j, dict_sorted.get(i, 0)]

        fig = plt.figure(figsize=(25, 20))
        ax = fig.add_subplot(2, 1, 2)
        dict_grab = dict(sorted(dict_grab.items()))
        with open('config.yaml') as f:
            dataframe = yaml.load(f, yaml.FullLoader)

        for i in dict_grab.keys():
            dict_grab[i].append(dataframe['dataframes'][str(i)][6:])
        list_of_KPD = [f'{round((i[1]/i[0])*100,2)}%' for i in dict_grab.values()]
        list_for_graphs_y1 = [i[0] for i in dict_grab.values()]
        list_for_graphs_y2 = [i[1] for i in dict_grab.values()]
        x_level = np.arange(len(list_for_graphs_y1))
        list_for_graphs_x = [i[2] for i in dict_grab.values()]

        grabs=ax.bar(x_level, list_for_graphs_y1, width=0.5, linewidth=2,
               yerr=2, label='Количество попыток захвата')
        ax.bar(x_level, list_for_graphs_y2, width=0.5, linewidth=2,
               yerr=2, label='Количество успешных захватов')
        for grab,text in zip(grabs,list_of_KPD):
            yval = grab.get_height()
            plt.text(grab.get_x() + grab.get_width() / 2, yval + 0.5, text, ha='center', va='bottom')
        ax.legend(loc=2)
        ax.set_xticks(x_level)
        ax.set_xticklabels(list_for_graphs_x, rotation=20, ha='right')
        ax.grid()
        x_label, y_label = self.make_axis(
            self.get_current_time("grab_attempt", "attempt_timestamp"))
        x_label_2, y_label_2 = self.make_axis(self.get_current_time(
            "grab_attempt", "attempt_timestamp", success=True))
        title = 'Общая статистика'
        fmt = dates.DateFormatter('%H:%M:%S')
        # Экземпляры фигуры и графика
        ax = fig.add_subplot(2, 1, 1)
        data_of_breaks = self.Executer.data_of_breaks(
            self.now_date_start, self.now_date_end)

        text = ''

        for i in data_of_breaks:
            if data_of_breaks[i][1]:

                timedelta = data_of_breaks[i][1]-i

                text += f'''{data_of_breaks[i][0]}, время ремонта:{timedelta.days*8 + timedelta.seconds//3600}ч,{
                    (timedelta.seconds % 3600)//60}м,{(timedelta.seconds % 3600) % 60}с\n'''
            else:
                text += f'{data_of_breaks[i][0]}, ремонт не закончен\n'
        # Отрисовка самих графиков
        ax.plot(x_label, y_label, '-.', color='g',
                label='Попыток захвата', markersize=1)
        ax.plot(x_label_2, y_label_2, "--", color='r', label='Успешный захват')
        # ax.plot([self.now_date_start,self.now_date_end], [0,0],'-.',color='black',markersize=1)
        if text:
            text = f'Поломки за {self.now_date}\n\n'+text
            ax.text(self.now_date_start, y_label[int(len(y_label)*0.8)], f'{text}', style='italic',
                    fontsize=10,
                    bbox={'facecolor': 'green',
                          'alpha': 0.6, 'pad': 2})
        if len(y_label) < 1:
            ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                         успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (len(y_label+1))) * 100:.2f}%''')
        else:
            ax.set_title(f'''{title}\nВсего захватов {y_label[-1]},
                         успешных захватов {y_label_2[-1]}.КПД {(y_label_2[-1] / (y_label[-1])) * 100:.2f}%''')
        ax.title.set_fontsize(10)
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(fmt)
        if len(x_label) > 0 and len(x_label_2) > 0:
            ax.set_xlim(min(x_label[0], x_label_2[0]),
                        max(x_label[-1], x_label_2[-1]))
        return fig

    def Save_PDF_images_grabs(self, flag: int = 0):
        """
        Функция создания массива графиков по запущенным тестам
        """
        test_id = self.Executer.get_test_id(
            self.now_date_start, self.now_date_end)

        # Парсинг данных по разным тестам робота (каждый запуск = новая порция датки)
        for idshnik in sorted(test_id):
            x_label, y_label = self.make_axis(self.get_current_time(
                "grab_attempt", "attempt_timestamp", idshnik))
            x_label_2, y_label_2 = self.make_axis(self.get_current_time(
                "grab_attempt", "attempt_timestamp", idshnik, True))
            if len(x_label) > 0 or len(x_label_2) > 0:
                flag += 1
            
            title = f'Статистика для опыта №{idshnik}'

            self.pdf.savefig(self.make_graph(
                x_label, x_label_2, y_label, y_label_2, title))

            time.sleep(0.1)

        self.pdf.savefig(self.Save_PDF_images_gisto())
        # Сохранение общего графика за сегодняшнюю дату

        self.pdf.close()
        if flag:
            return flag
        else:
            return None

    def Save_PDF_images_grabs_gisto(self, time_step: int = 1):
        plt.close('all')
        x_full = []
        x_succec = []
        y_full = []
        y_succel = []
        # Сохранение общего графика за сегодняшнюю дату

        full_worktime = self.get_current_time(
            "grab_attempt", "attempt_timestamp")
        second_worktime = self.get_current_time(
            "grab_attempt", "attempt_timestamp", success=True)

        # Не советую даже разбираться в этом.Должно работать. Если коротко - создает график скорости захватов(в минуту) от времени
        for i in np.arange(9, 20):
            y_full_sum = 0
            y_succes_sum = 0
            for k in range(0, 59, time_step):
                x_full.append((i+(k/60)))
                x_succec.append(i+(k/60))
                y_succes_sum = 0
                y_full_sum = 0
                for j in full_worktime:

                    if j > datetime.datetime.strptime(self.now_date_gisto+f"{i}:{k}:00",
                                                      "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(self.now_date_gisto+f"{i}:{k+time_step}:00",
                                                                                                              "%Y-%m-%d %H:%M:%S"):

                        y_full_sum += 1

                for j in second_worktime:

                    if j > datetime.datetime.strptime(self.now_date_gisto+f"{i}:{k}:00",
                                                      "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(self.now_date_gisto+f"{i}:{k+time_step}:00",
                                                                                                              "%Y-%m-%d %H:%M:%S"):
                        y_succes_sum += 1
                y_full.append(y_full_sum)
                y_succel.append(y_succes_sum)
        plt.rcParams["figure.figsize"] = (25, 15)
        plt.step(x_full, y_full, label='Общее количество попыток')
        plt.step(x_succec, y_succel, label='Количество успешных попыток')
        while 0 in y_full:
            y_full.remove(0)
        if len(x_full) and len(y_full):
            plt.step([x_full[0], x_full[-1]], [mean(y_full), mean(y_full)],
                     '--', label='Средняя скорость попыток захвата', color='b')
            try:
                plt.text(x_full[0], (mean(y_full)//10)*10 + 15,
                         f'{round(mean(y_full)*60, 2)} - попыток в час', fontsize=20)
            except Exception as e:
                print(e)
        while 0 in y_succel:
            y_succel.remove(0)
        if len(x_succec) and len(y_succel):
            plt.step([x_succec[0], x_succec[-1]], [mean(y_succel), mean(y_succel)],
                     '--', label='Средняя скорость успешных попыток захвата', color='orange')
            try:
                plt.text(x_succec[0], (mean(y_succel)//10)*10 + 5,
                         f'{round(mean(y_succel)*60, 2)} - успешных в час', fontsize=20)
            except Exception as e:
                print(e)
        plt.legend()
        plt.title(f"""Общее количество попыток {sum(y_full)}, количество успешных попыток {sum(y_succel)}.
    КПД {(sum(y_succel) / (1+sum(y_full))) * 100:.2f}%""")
        plt.grid(True)
        plt.xlabel("Время в часах")
        plt.ylabel("V,предметы/минута")

        plt.xlim(min(x_succec[0], x_full[0]), max(x_full[-1], x_succec[-1]))
        plt.ylim(0, 60)

        self.pdf2.savefig()

    def Save_PDF_images_odometr_gisto(self):
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
        fig.suptitle(f"Распределение нахождения робота по областям. Общее время работы - {sum((x_label)):.2f} мин. \n Пройденная дистанция - {d} м")
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



  
