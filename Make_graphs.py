import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages
from Make_folder import make_folder
import os
from setting import config
from DB_connection import make_connection
from verify_breaks import get_breaks
from statistics import mean

#list_of_breaks = get_breaks()
conn,cur=make_connection()

settings = config()

now_date_start = str(datetime.datetime.now().date()) + ' ' + '09:00:00.000000'
now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
now_date_end = str(datetime.datetime.now().date()) + ' ' + f'{datetime.datetime.now().time()}'
now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')

print(now_date_start)

#now_date_start = '2024-10-28' + ' ' + '09:00:00.000000'
#now_date_start = datetime.datetime.strptime(now_date_start, '%Y-%m-%d %H:%M:%S.%f')
#now_date_end = '2024-10-28' + ' ' + '21:00:00.000000'
#now_date_end = datetime.datetime.strptime(now_date_end, '%Y-%m-%d %H:%M:%S.%f')

now_date = datetime.date.today()
now_date_gisto = str(now_date)+" "
pdf = PdfPages(fr"{os.getcwd()}/Reports/{now_date}/Графики_по_тестам_{now_date}.pdf")
pdf2 = PdfPages(fr"{os.getcwd()}/Reports/{now_date}/Сводка_{now_date}.pdf")

def get_current_time(name_table: str, name_column: str=None, ID: int | None = None, date_start: str = now_date_start,
                          date_end: str = now_date_end):
    '''
    Функция служит для получения правильных (для отображения) осей х и у (В данной случае словаря, который позже преобразуется в другой функции). 
    На вход подается название таблицы, колонка в таблице, ID теста(служит для построения графиков по тестам).
    Даты начала и конца сортировки заданы по умолчанию как сегодняшняя дата
    На выходе получаются final_dict  для графиков matplotlib
    '''
    #Вариант, если строятся только графики по тестам. Ошибок в них быть не может, т.к. тест запускает, когда все проблемы устранены, а новые заводятся после остановки.
    if ID:
        #Первоначальный парсинг всех временных штампов исходя из условий номера теста и интересующей даты
        cur.execute(
        f"""SELECT {name_column} FROM {name_table}
        WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}' and test_id={ID}""")
        first_timestamp = [str(i[0].time())[0:-7] for i in cur.fetchall()]
        first_timestamp = [str(now_date)+' ' + i for i in first_timestamp]
        correct_timestamp = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]

        k=0
        correct_timestamp_dict_1 = {}
        for i in correct_timestamp:
            correct_timestamp_dict_1[i]=('work',k)
            k+=1
        sorted_dict = dict(sorted(correct_timestamp_dict_1.items()))
        final_dict = {}
        #Заполнение словарей в виде ключ(дата-время):значение(кортеж(режим,значение))
        for i,j in sorted_dict.items():
            if len(j)==3:
                if j[1]:
                    final_dict[i]=(j[0],j[2])
                    final_dict[j[1]]=(j[0],-100)
                else:
                    final_dict[i]=(j[0],j[2])
                    final_dict[now_date_end]=(j[0],-100)
            else:
                final_dict[i]=j
        final_dict = dict(sorted(final_dict.items()))
    #Вариант создания списков при построении общего графика
    else:

        #Парсинг значений с поломками
        cur.execute(f"""SELECT name_break,date_of_create_break,date_of_repair_break from breaks 
                    WHERE date_of_create_break<'{now_date_end}' AND (date_of_repair_break>'{now_date_start}' OR date_of_repair_break=NULL)""")
        #Составление словаря ключ(дата обнаружения поломки):значение(кортеж(название_поломки,дата починки, -100(значение по умолчанию для отображения на графике)))
        correct_timestamp_dict_2 = {i[1]:(i[0],i[2],-100) for i in cur.fetchall()}


        cur.execute(
        f"""SELECT {name_column} FROM {name_table} 
                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'""")
        first_timestamp = [str(i[0].time())[0:-7] for i in cur.fetchall()]
        first_timestamp = [str(now_date)+' ' + i for i in first_timestamp] 
        correct_timestamp = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]
        correct_timestamp=sorted(correct_timestamp)
        k=0
        correct_timestamp_dict_1 = {}
        correct_timestamp_2 = []
        for i in correct_timestamp:
            flagik = True
            for j in correct_timestamp_dict_2:
                if correct_timestamp_dict_2[j][1]:
                    if i>j and i<correct_timestamp_dict_2[j][1]:
                        flagik=False
                else:
                    if i>j:
                        flagik=False
            if flagik:
                correct_timestamp_2.append(i)
        #Создание словаря "рабочих" значений
        for i in correct_timestamp_2:
            correct_timestamp_dict_1[i]=('work',k,0)
            k+=1
        #Объединение двух словарей и сортировка их по возрастанию временных штампов
        full_dict = {**correct_timestamp_dict_1,**correct_timestamp_dict_2}
        full_dict=dict(sorted(full_dict.items()))
        final_dict = {}
        counter=1
        #Модернизация словаря, при котором добавляются промежуточные точки в начале и конце поломки. Нужно для правильного отображения на графиках
        
        for i in full_dict.keys():
            if not(full_dict[i][0]=='work'):
                if full_dict[i][1]:    
                    final_dict[i-datetime.timedelta(seconds=1)]=(full_dict[i][0],counter)
                    final_dict[i]=(full_dict[i][0],-100)
                    final_dict[full_dict[i][1]-datetime.timedelta(seconds=2)]=(full_dict[i][0],-100)
                    final_dict[full_dict[i][1]+datetime.timedelta(seconds=5)]=(full_dict[i][0],counter)
                else:
                    final_dict[i]=(full_dict[i][0],full_dict[i][2])
                    final_dict[i+datetime.timedelta(seconds=1)]=(full_dict[i][0],-100)
                    final_dict[now_date_end]=(full_dict[i][0],-100)
            else:
                final_dict[i]=(full_dict[i][0],full_dict[i][1])
                counter+=1
        #Окончательная сортировка данных по возрастанию временных штампов
        final_dict = dict(sorted(final_dict.items()))
    return final_dict

def make_axis(dict_data:dict):
    """
    Функция, преобразующая значения словаря, полученного из функции get_correct_time в оси x_label,y_label"""
    x_label = []
    y_label = []
    for i,j in dict_data.items():
        x_label.append(i)
        y_label.append(j[1])
    #for i,j in zip(x_label,y_label):
        #print(i,'---',j)
    return x_label,y_label


def make_graph(x_label:list,x_label_2,y_label:list,y_label_2:list,title):
    # Какой-то костыль, без которого не будет работать
    fmt = dates.DateFormatter('%H:%M:%S')

    # Экземпляры фигуры и графика
    fig, ax = plt.subplots()

    # Отрисовка самих графиков
    ax.plot(x_label, y_label,'-.',color='g',label='Попыток захвата',markersize=1)
    ax.plot(x_label_2,y_label_2, "--", color='r',label='Успешный захват')
    if len(y_label)<1:
        ax.set_title(f'''{title}\nВсего захватов {len(y_label)},успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label)+1)) * 100:.2f}%''')
    else:
        ax.set_title(f'''{title}\nВсего захватов {len(y_label)},успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label))) * 100:.2f}%''')
    ax.title.set_fontsize(10)
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(fmt)
    if len(x_label)>0 and len(x_label_2)>0:
        ax.set_xlim(min(x_label[0],x_label_2[0]),max(x_label[-1],x_label_2[-1]))

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

    list_for_graphs_y1 = [i[0] for i in dict_grab.values()]
    list_for_graphs_y2 = [i[1] for i in dict_grab.values()]
    x_level = np.arange(len(list_for_graphs_y1))
    list_for_graphs_x = [i[2] for i in dict_grab.values()]

    
    ax.bar(x_level,list_for_graphs_y1, width=0.5, linewidth=2, yerr=2,label='Количество попыток захвата')
    ax.bar(x_level,list_for_graphs_y2, width=0.5, linewidth=2, yerr=2,label='Количество успешных захватов')
    ax.legend(loc=2)
    ax.set_xticks(x_level)
    ax.set_xticklabels(list_for_graphs_x, rotation=20, ha='right')
    ax.grid()

    x_label,y_label=make_axis(get_current_time("grab_attempt", "attempt_timestamp"))
    x_label_2,y_label_2=make_axis(get_current_time("sorted_object", "sorted_timestamp"))
    title = 'Общая статистика'
    fmt = dates.DateFormatter('%H:%M:%S')
    # Экземпляры фигуры и графика
    ax = fig.add_subplot(2,1,1)
    cur.execute(f"""SELECT name_break,date_of_create_break,date_of_repair_break from breaks 
                    WHERE date_of_create_break<'{now_date_end}' AND (date_of_repair_break>'{now_date_start}' OR date_of_repair_break=NULL)""")
    text = ''
    
    for i in cur.fetchall():
        if i[2]:
            timedelta = i[2]-i[1]
            text+=f'{i[0]}, время ремонта:{timedelta.days*8 + timedelta.seconds//3600}ч,{(timedelta.seconds%3600)//60}м,{(timedelta.seconds%3600)%60}с\n'
        else:
            text+=f'{i[0]}, ремонт не закончен\n'
    # Отрисовка самих графиков
    ax.plot(x_label, y_label,'-.',color='g',label='Попыток захвата',markersize=1)
    ax.plot(x_label_2, y_label_2, "--", color='r',label='Успешный захват')
    ax.plot([now_date_start,now_date_end], [0,0],'-.',color='black',markersize=1)
    if text:
        text=f'Поломки за {now_date}\n\n'+text
        ax.text(now_date_start,y_label[int(len(y_label)*0.8)],f'{text}',style ='italic', 
        fontsize = 10, 
        bbox ={'facecolor':'green', 
               'alpha':0.6, 'pad':2})
    if len(y_label)<1:
        ax.set_title(f'''{title}\nВсего захватов {len(y_label)},успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label)+1)) * 100:.2f}%''')
    else:
        ax.set_title(f'''{title}\nВсего захватов {len(y_label)},успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label))) * 100:.2f}%''')
    ax.title.set_fontsize(10)
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(fmt)
    if len(x_label)>0 and len(x_label_2)>0:
        ax.set_xlim(now_date_start,max(x_label[-1],x_label_2[-1]))
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
        x_label,y_label=make_axis(get_current_time("grab_attempt", "attempt_timestamp", ID))
        x_label_2,y_label_2=make_axis(get_current_time("sorted_object", "sorted_timestamp", ID))
        if len(x_label)>0 or len(x_label_2)>0:
            flag+=1
        title = f'Статистика для опыта №{ID}'
        
        pdf.savefig(make_graph(x_label,x_label_2,y_label,y_label_2,title))
    pdf.savefig(Save_PDF_images_gisto())
    # Сохранение общего графика за сегодняшнюю дату

    pdf.close()
    if flag:
        return flag
    else:
        return None


def Save_PDF_images_grabs_gisto(time_step:int=1):
    plt.close('all')
    x_full = []
    x_succec = []
    y_full = []
    y_succel = []
    # Сохранение общего графика за сегодняшнюю дату
    
    full_worktime = get_current_time("grab_attempt", "attempt_timestamp")
    second_worktime = get_current_time("sorted_object", "sorted_timestamp")
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
                                                "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(now_date_gisto+f"{i}:{k+time_step}:00",
                                                                                                "%Y-%m-%d %H:%M:%S"):
                
                    y_full_sum += 1
                    
            for j in second_worktime:
                

                if j > datetime.datetime.strptime(now_date_gisto+f"{i}:{k}:00",
                                                "%Y-%m-%d %H:%M:%S") and j < datetime.datetime.strptime(now_date_gisto+f"{i}:{k+time_step}:00",
                                                                                                "%Y-%m-%d %H:%M:%S"):
                    y_succes_sum += 1
            y_full.append(y_full_sum)
            y_succel.append(y_succes_sum)
    plt.rcParams["figure.figsize"] = (25,15)
    plt.step(x_full, y_full, label='Общее количество попыток')
    plt.step(x_succec, y_succel, label='Количество успешных попыток')
    while 0 in y_full:
        y_full.remove(0)
    if len(x_full) and len(y_full):
        plt.step([x_full[0],x_full[-1]],[mean(y_full),mean(y_full)],'--',label='Средняя скорость попыток захвата',color='b')
    while 0 in y_succel:
        y_succel.remove(0)
    if len(x_succec) and len(y_succel):    
        plt.step([x_succec[0],x_succec[-1]],[mean(y_succel),mean(y_succel)],'--',label='Средняя скорость успешных попыток захвата',color='orange')
    plt.legend()
    plt.title(f"""Общее количество попыток {sum(y_full)}, количество успешных попыток {sum(y_succel)}.
КПД {(sum(y_succel) / (1+sum(y_full))) * 100:.2f}%""")
    plt.grid(True)
    plt.xlabel("Время в часах")
    plt.ylabel("V,предметы/минута")
    plt.xlim(9,21)
    
    pdf2.savefig()
    pdf2.close()





if __name__ == '__main__':
    make_folder(True)
    make_folder()
    Save_PDF_images_gisto()
    a=Save_PDF_images_grabs()

