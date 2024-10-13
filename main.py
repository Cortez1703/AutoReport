import datetime
import numpy as np
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
from Make_folder import make_folder

conn = 2
cur = conn.cursor()

# now_date_start = str(datetime.datetime.now().date()) + ' ' + '00:00:00.000000'
# now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
# now_date_end = str(datetime.datetime.now().date()) + ' ' + '23:59:59.999999'
# now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')

now_date_start = '2024-10-11' + ' ' + '09:00:00.000000'
now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
now_date_end = '2024-10-11' + ' ' + '23:59:59.999999'
now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')

now_date = datetime.date.today()
pdf = PdfPages(fr"C:\Users\aleks\PycharmProjects\AutoGeneration\Reports\{now_date}\Графики_по_тестам_{now_date}.pdf")
pdf2 = PdfPages(fr"C:\Users\aleks\PycharmProjects\AutoGeneration\Reports\{now_date}\Сводка_{now_date}.pdf")


def get_correct_timestamp(name_table: str, name_column: str, ID: int | None = None, date_start: str = now_date_start,
                          date_end: str = now_date_end):
    """Функция, возращающая список временных констант для формирования графика

    output:
    correct_timestamp : list[datetime.time] (format "%H:%M:%S")
    """

    if ID:
        cur.execute(
            f"""SELECT {name_column} FROM {name_table} 
            WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}' and test_id={ID}""")
        first_timestamp = [str(i[0].time())[0:-7] for i in cur.fetchall()]
        correct_timestamp = [datetime.datetime.strptime(i, "%H:%M:%S") for i in first_timestamp]
    else:
        cur.execute(
            f"""SELECT {name_column} FROM {name_table} 
                    WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'""")
        first_timestamp = [str(i[0].time())[0:-7] for i in cur.fetchall()]
        correct_timestamp = [datetime.datetime.strptime(i, "%H:%M:%S") for i in first_timestamp]
    return correct_timestamp


def make_graph(full_worktime: list, second_worktime: list):
    # Какой-то костыль, без которого не будет работать
    fmt = dates.DateFormatter('%H:%M:%S')

    # Экземпляры фигуры и графика
    fig, ax = plt.subplots()
    Y_full = np.linspace(0, len(full_worktime) - 1, len(full_worktime))
    Y_succesful_grab = np.linspace(0, len(second_worktime) - 1, len(second_worktime))

    # Отрисовка самих графиков
    ax.plot(full_worktime, Y_full, "-o", label='Попыток захвата')
    ax.plot(second_worktime, Y_succesful_grab, "-o", label='Успешный захват')

    ax.set_title(f'''Всего захватов {len(full_worktime)}, успешных захватов {len(second_worktime)}.
                КПД {(len(second_worktime) / (len(full_worktime))) * 100:.2f}%''')
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()

    return fig


def Save_PDF_images_grabs():
    """Функция создает PDF-файл с интересующими графиками

    Output:
    PDF-file with images
    """
    cur.execute(
        f"SELECT test_id FROM grab_attempt WHERE attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}'")
    test_id = [i[0] for i in set(cur.fetchall()) if bool(i[0]) == True]

    # Парсинг данных по разным тестам робота (каждый запуск = новая порция датки)
    for ID in test_id:
        full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp", ID)
        second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp", ID)
        pdf.savefig(make_graph(full_worktime, second_worktime))
        print(ID)

    # Сохранение общего графика за сегодняшнюю дату
    full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp")
    second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp")
    pdf.savefig(make_graph(full_worktime, second_worktime))
    pdf.close()


def Save_PDF_images_grabs_gisto():
    plt.close('all')
    x_full = []
    x_succec = []
    y_full = []
    y_succel = []
    # Сохранение общего графика за сегодняшнюю дату
    full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp")
    second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp")
    for i in range(9, 20):
        y_full_sum = 0
        y_succes_sum = 0
        x_full.append(i)
        x_succec.append(i)
        for j in full_worktime:
            if j > datetime.datetime.strptime(f"{i}:00:00",
                                              "%H:%M:%S") and j < datetime.datetime.strptime(f"{i + 1}:00:00",
                                                                                             "%H:%M:%S"):
                y_full_sum += 1
        for j in second_worktime:
            if j > datetime.datetime.strptime(f"{i}:00:00", "%H:%M:%S") and j < datetime.datetime.strptime(
                    f"{i + 1}:00:00", "%H:%M:%S"):
                y_succes_sum += 1
        y_full.append(y_full_sum)
        y_succel.append(y_succes_sum)
    plt.step(x_full, y_full, label='Общее количество попыток')
    plt.step(x_succec, y_succel, label='Количество успешных попыток')
    plt.legend()
    plt.title(f"""Общее количество попыток {sum(y_full)}, количество успешных попыток {sum(y_succel)}.
КПД {(sum(y_succel) / sum(y_full)) * 100:.2f}%""")
    plt.grid(True)
    plt.xlabel("Время в часах")
    plt.ylabel("V,предметы/час")
    pdf2.savefig()
    pdf2.close()


if __name__ == '__main__':
    make_folder(True)
    make_folder()
    Save_PDF_images_grabs()
    Save_PDF_images_grabs_gisto()
