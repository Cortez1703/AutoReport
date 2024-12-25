#Standart imports
import datetime


class Creater:

    def __init__(self,cur,con,Ex):
        self.cur = cur
        self.con = con
        self.Executer=Ex
        self.now_date_start = str(datetime.datetime.now().date()) + ' ' + '09:00:00.000000'
        self.now_date_start = datetime.datetime.strptime(self.now_date_start, '%Y-%m-%d %H:%M:%S.%f')
        #self.now_date_start = str(datetime.datetime.now().date()) + ' ' + '09:00:00.000000'
        #self.now_date_start = datetime.datetime.strptime(self.now_date_start, '%Y-%m-%d %H:%M:%S.%f')
        self.now_date_end = str(datetime.datetime.now().date()) + ' ' + f'{datetime.datetime.now().time()}'
        self.now_date_end = datetime.datetime.strptime(self.now_date_end, '%Y-%m-%d %H:%M:%S.%f')
        #self.now_date_start = '2024-11-15' + ' ' + '09:01:02.000000'
        #self.now_date_start = datetime.datetime.strptime(self.now_date_start, '%Y-%m-%d %H:%M:%S.%f')
        #self.now_date_end = '2024-11-15' + ' ' + '21:01:02.000000'
        #self.now_date_end = datetime.datetime.strptime(self.now_date_end, '%Y-%m-%d %H:%M:%S.%f')

        self.now_date = datetime.date.today()
        self.now_date_gisto = str(self.now_date)+" "

    
    def get_current_time(self, name_column:str,name_table:str,ID:int|None=None) -> dict:
        '''
        Функция служит для получения правильных (для отображения) осей х и у (В данной случае словаря, который позже преобразуется в другой функции). 
        На вход подается название таблицы, колонка в таблице, ID теста(служит для построения графиков по тестам).
        Даты начала и конца сортировки заданы по умолчанию как сегодняшняя дата
        На выходе получаются final_dict  для графиков matplotlib
        '''
        if ID:
            #Первоначальный парсинг всех временных штампов исходя из условий номера теста и интересующей даты
            correct_timestamp=self.Executer.data_for_graphs(name_column,name_table,self.now_date_start,self.now_date_end)
            sorted_dict = self._make_work_dict(correct_timestamp)
            final_dict = self._make_full_dict(sorted_dict)

        #Вариант создания списков при построении общего графика
        else:
            dict_of_breaks_1 = self.Executer.data_of_breaks(self.now_date_start,self.now_date_end)
            list_of_works_1  = self.Executer.data_for_graphs(name_column,name_table,self.now_date_start,self.now_date_end)
            k=0
            correct_dict_of_work = {}
            #Создание словаря "рабочих" значений
            for i in self._make_correct_list_of_work(list_of_works_1,dict_of_breaks_1):
                correct_dict_of_work[i]=('work',k,0)
                k+=1
            #Объединение двух словарей и сортировка их по возрастанию временных штампов
            full_dict=dict(sorted({**dict_of_breaks_1,**correct_dict_of_work}.items()))
            final_dict = self._final_dict_without_id(full_dict,self.now_date_end)
        return final_dict

    
    def _make_work_dict(self,list_of_data:list) -> dict:
        k=0
        dict_of_work_data = {}
        for i in list_of_data:
            dict_of_work_data[i]=('work',k)
            k+=1
        sorted_dict = dict(sorted(dict_of_work_data.items()))
        return sorted_dict
    
    def _make_full_dict(self,work_dict:dict):
        final_dict = {}
        #Заполнение словарей в виде ключ(дата-время):значение(кортеж(режим,значение))
        for i,j in work_dict.items():
            if len(j)==3:
                if j[1]:
                    final_dict[i]=(j[0],j[2])
                    final_dict[j[1]]=(j[0],-100)
                else:
                    final_dict[i]=(j[0],j[2])
                    final_dict[self.now_date_end]=(j[0],-100)
            else:
                final_dict[i]=j
        final_dict = dict(sorted(final_dict.items()))
        return final_dict
    
    def _make_correct_list_of_work(self,list_of_work_timestamp,dict_of_breaks):
        
        correct_list_of_work= []
        for i in list_of_work_timestamp:
            flagik = True
            for j in dict_of_breaks:
                if dict_of_breaks[j][1]:
                    if i>j and i<dict_of_breaks[j][1]:
                        flagik=False
                else:
                    if i>j:
                        flagik=False
            if flagik:
                correct_list_of_work.append(i)
        return correct_list_of_work
    
    def _final_dict_without_id(self,full_dict:dict,now_date_end):
        counter = 1
        final_dict = {}
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
    
    def make_axis(self,dict_data:dict):
        """
        Функция, преобразующая значения словаря, полученного из функции get_correct_time в оси x_label,y_label"""
        x_label = []
        y_label = []
        for i,j in dict_data.items():
            x_label.append(i)
            y_label.append(j[1])
        return x_label,y_label