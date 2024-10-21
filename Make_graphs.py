import datetime
import numpy as np
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
from Make_folder import make_folder
import os
from setting import config


settings = config()
conn = psycopg2.connect(dbname = settings.DB_CONFIG['dbname'],
    user=settings.DB_CONFIG['user'],
    password=settings.DB_CONFIG['password'],
    host=settings.DB_CONFIG['host'],
    port=settings.DB_CONFIG['port']
)
cur = conn.cursor()



now_date_start = str(datetime.datetime.now().date()) + ' ' + '09:00:00.000000'
now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
now_date_end = str(datetime.datetime.now().date()) + ' ' + f'{datetime.datetime.now().time()}'
now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')



#now_date_start = '2024-10-15' + ' ' + '09:00:00.000000'
#now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
#now_date_end = '2024-10-15' + ' ' + '21:00:00.000000'
#now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')

now_date = datetime.date.today()
now_date_gisto = str(now_date)+" "
pdf = PdfPages(fr"{os.getcwd()}/Reports/{now_date}/Графики_по_тестам_{now_date}.pdf")
pdf2 = PdfPages(fr"{os.getcwd()}/Reports/{now_date}/Сводка_{now_date}.pdf")



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
        first_timestamp = [str(now_date)+' ' + i for i in first_timestamp] 
        correct_timestamp = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]
    else:
        cur.execute(
            f"""SELECT {name_column} FROM {name_table} 
                    WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'""")
        first_timestamp = [str(i[0].time())[0:-7] for i in cur.fetchall()]
        first_timestamp = [str(now_date)+' ' + i for i in first_timestamp] 
        correct_timestamp = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]
    
    return correct_timestamp
    


def make_graph(full_worktime: list, second_worktime: list,title:str):
    # Какой-то костыль, без которого не будет работать
    fmt = dates.DateFormatter('%H:%M:%S')

    # Экземпляры фигуры и графика
    fig, ax = plt.subplots()
    Y_full = np.linspace(0, len(full_worktime) - 1, len(full_worktime))
    Y_succesful_grab = np.linspace(0, len(second_worktime) - 1, len(second_worktime))

    # Отрисовка самих графиков
    ax.plot(full_worktime, Y_full,'-.',color='g',label='Попыток захвата',markersize=1)
    ax.plot(second_worktime, Y_succesful_grab, "--", color='r',label='Успешный захват')
    if len(full_worktime)<1:
        ax.set_title(f'''{title}\nВсего захватов {len(full_worktime)},успешных захватов {len(second_worktime)}.КПД {(len(second_worktime) / (len(full_worktime)+1)) * 100:.2f}%''')
    else:
        ax.set_title(f'''{title}\nВсего захватов {len(full_worktime)},успешных захватов {len(second_worktime)}.КПД {(len(second_worktime) / (len(full_worktime))) * 100:.2f}%''')
    ax.title.set_fontsize(10)
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(fmt)
    if len(full_worktime)>0 and len(second_worktime)>0:
        ax.set_xlim(min(full_worktime[0],second_worktime[0]),max(full_worktime[-1],second_worktime[-1]))

    fig.autofmt_xdate()
    
    return fig


def Save_PDF_images_gisto():
    dict_grab = {}
    dict_sorted = {}
    cur.execute(f"SELECT category_id from grab_attempt where attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}'") 
    list_of_category_grab = [i[0] for i in cur.fetchall()]
    cur.execute(f"SELECT category_id from sorted_object where sorted_timestamp>'{now_date_start}' and sorted_timestamp<'{now_date_end}'") 
    list_of_category_sorted = [i[0] for i in cur.fetchall()]
    for i in set(list_of_category_grab):
        dict_grab[i]=list_of_category_grab.count(i)
    for i in set(list_of_category_sorted):
        dict_sorted[i]=list_of_category_sorted.count(i)

    for i,j in dict_grab.items():
        dict_grab[i]=[j,dict_sorted.get(i,0)]

    fig = plt.figure(figsize=(25, 20))
    ax = fig.add_subplot(2,1,2)
    dict_grab=dict(sorted(dict_grab.items()))
    dataframe = settings.dataframes

    for i in dict_grab.keys():
        dict_grab[i].append(dataframe[str(i)][6:])
        print(dataframe[str(i)])
    list_for_graphs_y1 = [i[0] for i in dict_grab.values()]
    list_for_graphs_y2 = [i[1] for i in dict_grab.values()]
    x_level = np.arange(len(list_for_graphs_y1))
    list_for_graphs_x = [i[2] for i in dict_grab.values()]
    print(dict_grab)
    #list_for_graphs_x=sorted(list_for_graphs_x)
    #list_for_graphs_x = [str(i) for i in list_for_graphs_x]

    ax.bar(x_level,list_for_graphs_y1, width=0.5, linewidth=2, yerr=2,label='Количество попыток захвата')
    ax.bar(x_level,list_for_graphs_y2, width=0.5, linewidth=2, yerr=2,label='Количество успешных захватов')
    ax.legend(loc=2)
    ax.set_xticks(x_level)
    ax.set_xticklabels(list_for_graphs_x, rotation=20, ha='right')
    ax.grid()

    full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp")
    second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp")
    title = 'Общая статистика'

    fmt = dates.DateFormatter('%H:%M:%S')

    # Экземпляры фигуры и графика
    ax = fig.add_subplot(2,1,1)
    Y_full = np.linspace(0, len(full_worktime) - 1, len(full_worktime))
    Y_succesful_grab = np.linspace(0, len(second_worktime) - 1, len(second_worktime))

    # Отрисовка самих графиков
    ax.plot(full_worktime, Y_full,'-.',color='g',label='Попыток захвата',markersize=1)
    ax.plot(second_worktime, Y_succesful_grab, "--", color='r',label='Успешный захват')
    if len(full_worktime)<1:
        ax.set_title(f'''{title}\nВсего захватов {len(full_worktime)},успешных захватов {len(second_worktime)}.КПД {(len(second_worktime) / (len(full_worktime)+1)) * 100:.2f}%''')
    else:
        ax.set_title(f'''{title}\nВсего захватов {len(full_worktime)},успешных захватов {len(second_worktime)}.КПД {(len(second_worktime) / (len(full_worktime))) * 100:.2f}%''')
    ax.title.set_fontsize(10)
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(fmt)
    if len(full_worktime)>0 and len(second_worktime)>0:
        ax.set_xlim(min(full_worktime[0],second_worktime[0]),max(full_worktime[-1],second_worktime[-1]))
    return fig

def Save_PDF_images_grabs(flag:int=0):
    """Функция создает PDF-файл с интересующими графиками

    Output:
    PDF-file with images
    """
    cur.execute(
        f"SELECT test_id FROM grab_attempt WHERE attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}'")
    test_id = [i[0] for i in set(cur.fetchall()) if bool(i[0]) == True]

    # Парсинг данных по разным тестам робота (каждый запуск = новая порция датки)
    for ID in sorted(test_id):
        full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp", ID)
        second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp", ID)
        if len(full_worktime)>0 or len(second_worktime)>0:
            flag+=1
        title = f'Статистика для опыта №{ID}'
        
        pdf.savefig(make_graph(full_worktime, second_worktime,title))
    pdf.savefig(Save_PDF_images_gisto())
    # Сохранение общего графика за сегодняшнюю дату

    pdf.close()
    if flag:
        return flag


def Save_PDF_images_grabs_gisto(time_step:int=1):
    plt.close('all')
    x_full = []
    x_succec = []
    y_full = []
    y_succel = []
    # Сохранение общего графика за сегодняшнюю дату
    full_worktime = get_correct_timestamp("grab_attempt", "attempt_timestamp")
    second_worktime = get_correct_timestamp("sorted_object", "sorted_timestamp")
    for i in np.arange (9, 20):
        y_full_sum = 0
        y_succes_sum = 0
        for k in range(0,59,time_step):
            x_full.append((i+(k/60)))
            x_succec.append(i+(k/60))
            y_succes_sum=0
            y_full_sum=0
            for j in full_worktime:
                
                if j > datetime.datetime.strptime(now_date_gisto+f"{i}:{k}:00",
                                                "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(now_date_gisto+f"{i}:{k+1}:00",
                                                                                                "%Y-%m-%d %H:%M:%S"):
                
                    y_full_sum += 1

            for j in second_worktime:
                

                if j > datetime.datetime.strptime(now_date_gisto+f"{i}:{k}:00",
                                                "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(now_date_gisto+f"{i}:{k+1}:00",
                                                                                                "%Y-%m-%d %H:%M:%S"):
                    y_succes_sum += 1
            y_full.append(y_full_sum)
            y_succel.append(y_succes_sum)
            
    plt.step(x_full, y_full, label='Общее количество попыток')
    plt.step(x_succec, y_succel, label='Количество успешных попыток')
    plt.legend()
    plt.title(f"""Общее количество попыток {sum(y_full)}, количество успешных попыток {sum(y_succel)}.
КПД {(sum(y_succel) / (1+sum(y_full))) * 100:.2f}%""")
    plt.grid(True)
    plt.xlabel("Время в часах")
    plt.ylabel("V,предметы/час")
    plt.xlim(9,21)
    
    pdf2.savefig()
    pdf2.close()


if __name__ == '__main__':
    make_folder(True)
    make_folder()
    a=Save_PDF_images_grabs()
    b=Save_PDF_images_grabs_gisto()
