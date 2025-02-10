# Standart imports
import datetime
from Logic.Executer import Executer
from Logic.DB_connection import make_connection
from matplotlib import pyplot as plt
import matplotlib.dates as dates
con,cur=make_connection()

class Creater():

    def __init__(self, cur, con,deltaDays=0):
        self.Executer = Executer(cur,con)
        self.now_date_start = datetime.datetime.combine(datetime.datetime.now().date()-datetime.timedelta(days=deltaDays), datetime.time(9, 0, 0))
        self.now_date_end = datetime.datetime.combine(datetime.datetime.now().date()-datetime.timedelta(days=deltaDays), datetime.time(21, 0, 0))

    def make_right_odometr(self,data):
        """
        Выдает данные для построения распределения Гаусса/пройденного расстояния
        """
        end_list = []
        match data:
            case int():
                return data
            case _:
                first_start = True
                for info in data:
                    if first_start:
                        end_list = [int(i)*0.05/60 for i in info]
                        first_start = False
                    else:
                        for i in range(0,len(info)):
                            end_list[i] += int(info[i])*0.05/60
                return end_list


    def get_current_time(self, name_column: str, name_table: str, ID: int | None = None, success: bool | None = None) -> dict:
        '''
        Формирует конечные оси для графиков

        Optional:

        ID - если True - оси для графика по тесту. Отображение ошибок не будет
        success - True=успешные захваты.
        '''
        
        match ID:

            case int():
                return self.Executer.axis_standart_graph(name_column, name_table, self.now_date_start, self.now_date_end, ID, success)
            
            case _:
                xArrayFinal = []
                yArrayFinal = []
                Counter = 0
                xArray,yArray = self.Executer.axis_standart_graph(name_column, name_table, self.now_date_start, self.now_date_end, ID, success)
                breakArray = self.Executer.data_of_breaks(self.now_date_start,self.now_date_end)

                if breakArray:
                    for breakTime in breakArray:
                        while xArray[Counter]<breakTime[1]:
                            xArrayFinal.append(xArray[Counter])
                            yArrayFinal.append(Counter)
                            Counter+=1

                        if breakTime[2]:
                            if xArray[-1]<breakTime[2]:
                                xArrayFinal.append(breakTime[1])
                                yArrayFinal.append(-100)
                                xArrayFinal.append(breakTime[2])
                                yArrayFinal.append(-100)
                                xArrayFinal.append(breakTime[2]+datetime.timedelta(seconds=1))
                                yArrayFinal.append(yArray[-1])
                                return xArrayFinal,yArrayFinal
                            while xArray[Counter]<breakTime[2]:
                                Counter+=1
                            xArrayFinal.append(breakTime[1])
                            yArrayFinal.append(-100)
                            xArrayFinal.append(breakTime[2])
                            yArrayFinal.append(-100)
                            xArrayFinal.append(xArray[Counter]-datetime.timedelta(microseconds=1))
                            yArrayFinal.append(-100)
                            xArrayFinal.append(xArray[Counter])
                            yArrayFinal.append(Counter)
                            Counter+=1
                        else:
                            return xArrayFinal,yArrayFinal
                    while Counter<(len(xArray)-1):
                        
                        xArrayFinal.append(xArray[Counter])
                        yArrayFinal.append(Counter)
                        Counter+=1
                    return xArrayFinal,yArrayFinal
                else:
                    return xArray,yArray

    def make_axis(self, dict_data: dict):
        """
        Функция, преобразующая значения словаря, полученного из функции get_correct_time в оси x_label,y_label"""
        x_label = []
        y_label = []
        for i, j in dict_data.items():
            x_label.append(i)
            y_label.append(j[1])
        return x_label, y_label

    
