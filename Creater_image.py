#Matplotlib/NumPy imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_pdf import PdfPages

#Local imports
from Creater_right_data import Creater
from statistics import mean
from Make_folder import make_folder
from Executer import Executer as Ex
from DB_connection import make_connection


#Standart imports
import datetime
import os
import yaml

Executer = Ex()
connection,cursor=make_connection()

class Creater_image(Creater):
    
    """
        Конструктор для создания и сохранения графиков в пдф
    """

    def __init__(self,cur,con,Exec):
        super().__init__(cur,con,Exec)
        self.now_date = datetime.date.today()
        self.pdf = PdfPages(fr"{os.getcwd()}/Reports/{self.now_date}/Графики_по_тестам_{self.now_date}.pdf")
        self.pdf2 = PdfPages(fr"{os.getcwd()}/Reports/{self.now_date}/Сводка_{self.now_date}.pdf")
              

    def make_graph(self,x_label:list,x_label_2,y_label:list,y_label_2:list,title:str):
        """
        Функция, используемая для создания общего графика работы за раб.день
        """
    # Какой-то костыль, без которого не будет работать
        fmt = dates.DateFormatter('%H:%M:%S')

        # Экземпляры фигуры и графика
        fig, ax = plt.subplots()

        # Отрисовка самих графиков
        ax.plot(x_label, y_label,'-.',color='g',label='Попыток захвата',markersize=1)
        ax.plot(x_label_2,y_label_2, "--", color='r',label='Успешный захват')
        if len(y_label)<1:
            ax.set_title(f'''{title}\nВсего захватов {len(y_label)},
                         успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label)+1)) * 100:.2f}%''')
        else:
            ax.set_title(f'''{title}\nВсего захватов {len(y_label)},
                         успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label))) * 100:.2f}%''')
        ax.title.set_fontsize(10)
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(fmt)
        if len(x_label)>0 and len(x_label_2)>0:
            ax.set_xlim(min(x_label[0],x_label_2[0]),max(x_label[-1],x_label_2[-1]))

        fig.autofmt_xdate()
        
        return fig
    

    def Save_PDF_images_gisto(self):
        fmt = dates.DateFormatter('%H:%M:%S')
        """
        Функция для создания общего графика по категориям за день
        """
        dict_grab = {}
        dict_sorted = {} 
        list_of_category_grab,list_of_category_sorted = self.Executer.data_of_sorted(self.now_date_start,self.now_date_end)

        #Добавление количества включений той или иной категории
        for i in set(list_of_category_grab):
            dict_grab[i]=list_of_category_grab.count(i)
        for i in set(list_of_category_sorted):
            dict_sorted[i]=list_of_category_sorted.count(i)

        #Составление словаря ключ(категория):значение(всего попыток,успешных|0)
        for i,j in dict_grab.items():
            dict_grab[i]=[j,dict_sorted.get(i,0)]

        fig = plt.figure(figsize=(25, 20))
        ax = fig.add_subplot(2,1,2)
        dict_grab=dict(sorted(dict_grab.items()))
        with open('config.yaml') as f:
            dataframe = yaml.load(f,yaml.FullLoader)

        for i in dict_grab.keys():
            dict_grab[i].append(dataframe['dataframes'][str(i)][6:])

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
        x_label,y_label = self.make_axis(self.get_current_time("grab_attempt", "attempt_timestamp"))
        x_label_2,y_label_2 = self.make_axis(self.get_current_time("sorted_object", "sorted_timestamp"))
        title = 'Общая статистика'
        fmt = dates.DateFormatter('%H:%M:%S')
        # Экземпляры фигуры и графика
        ax = fig.add_subplot(2,1,1)
        data_of_breaks = self.Executer.data_of_breaks(self.now_date_start,self.now_date_end)
        print(data_of_breaks)
        text = ''
        
        for i in data_of_breaks:
            if data_of_breaks[i][1]:
                
                timedelta = data_of_breaks[i][1]-i
                print(timedelta.days)
                print(timedelta.seconds//3600)
                text+=f'{data_of_breaks[i][0]}, время ремонта:{timedelta.days*8 + timedelta.seconds//3600}ч,{(timedelta.seconds%3600)//60}м,{(timedelta.seconds%3600)%60}с\n'
            else:
                text+=f'{data_of_breaks[i][0]}, ремонт не закончен\n'
        # Отрисовка самих графиков
        ax.plot(x_label, y_label,'-.',color='g',label='Попыток захвата',markersize=1)
        ax.plot(x_label_2, y_label_2, "--", color='r',label='Успешный захват')
        #ax.plot([self.now_date_start,self.now_date_end], [0,0],'-.',color='black',markersize=1)
        if text:
            text=f'Поломки за {self.now_date}\n\n'+text
            ax.text(self.now_date_start,y_label[int(len(y_label)*0.8)],f'{text}',style ='italic', 
            fontsize = 10, 
            bbox ={'facecolor':'green', 
                'alpha':0.6, 'pad':2})
        if len(y_label)<1:
            ax.set_title(f'''{title}\nВсего захватов {len(y_label)},
                         успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label)+1)) * 100:.2f}%''')
        else:
            ax.set_title(f'''{title}\nВсего захватов {len(y_label)},
                         успешных захватов {len(y_label_2)}.КПД {(len(y_label_2) / (len(y_label))) * 100:.2f}%''')
        ax.title.set_fontsize(10)
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(fmt)
        if len(x_label)>0 and len(x_label_2)>0:
            ax.set_xlim(self.now_date_start,max(x_label[-1],x_label_2[-1]))
        return fig
    
    def Save_PDF_images_grabs(self,flag:int=0):
        """
        Функция создания массива графиков по запущенным тестам
        """
        test_id = self.Executer.get_test_id(self.now_date_start,self.now_date_end)

        # Парсинг данных по разным тестам робота (каждый запуск = новая порция датки)
        for idshnik in sorted(test_id):
            x_label,y_label=self.make_axis(self.get_current_time("grab_attempt", "attempt_timestamp", idshnik))
            x_label_2,y_label_2=self.make_axis(self.get_current_time("sorted_object", "sorted_timestamp", idshnik))
            if len(x_label)>0 or len(x_label_2)>0:
                flag+=1
            title = f'Статистика для опыта №{idshnik}'
            
            self.pdf.savefig(self.make_graph(x_label,x_label_2,y_label,y_label_2,title))
        self.pdf.savefig(self.Save_PDF_images_gisto())
        # Сохранение общего графика за сегодняшнюю дату

        self.pdf.close()
        if flag:
            return flag
        else:
            return None
        
    def Save_PDF_images_grabs_gisto(self,time_step:int=1):
        plt.close('all')
        x_full = []
        x_succec = []
        y_full = []
        y_succel = []
        # Сохранение общего графика за сегодняшнюю дату
        
        full_worktime = self.get_current_time("grab_attempt", "attempt_timestamp")
        second_worktime = self.get_current_time("sorted_object", "sorted_timestamp")

        #Не советую даже разбираться в этом.Должно работать. Если коротко - создает график скорости захватов(в минуту) от времени
        for i in np.arange (9, 20):
            y_full_sum = 0
            y_succes_sum = 0
            for k in range(0,59,time_step):
                x_full.append((i+(k/60)))
                x_succec.append(i+(k/60))
                y_succes_sum=0
                y_full_sum=0
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
        
        self.pdf2.savefig()
        self.pdf2.close()

if __name__=='__main__':
    testclass = Creater_image(cursor,connection,Executer)
    make_folder(True)
    make_folder()
    testclass.Save_PDF_images_gisto()
    a=testclass.Save_PDF_images_grabs()