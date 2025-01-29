from DB_connection import make_connection
import datetime

connection, cursor = make_connection()


class Executer:

    def __init__(self, cur=cursor, con=connection):
        self.cur = cur
        self.con = con
        self.now_date = datetime.date.today()

    def data_for_graphs(self, name_table: str, name_column: str, date_start: str, date_end: str, ID: int | None = None, success: bool | None = None) -> list | None:
        """
        Формирование правильного массива времен для графиков. Два варианта:
        1) Если указан ID - формирование оси Х по id-тесту
        2) Если не указан ID - формирование оси Х для общего графика за день
        На вход принимает :
        - Имя таблицы
        - Столбец(...-timestamp)
        - Время начала
        - Время конца
        - ID(optional)
        """

        # Формирование по ID
        if ID:
            if success:
                self.cur.execute(
                    f"""SELECT {name_column} FROM {name_table}
                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}' and test_id={ID} and success={success}""")
            else:
                self.cur.execute(
                    f"""SELECT {name_column} FROM {name_table}
                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}' and test_id={ID} """)

            first_timestamp = [str(i[0].time())[0:-7]
                               for i in self.cur.fetchall()]
            first_timestamp = [str(self.now_date)+' ' +
                               i for i in first_timestamp]
            list_of_data = [datetime.datetime.strptime(
                i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]

        # Формирование по всей оси времени
        else:
            if success:
                self.cur.execute(
                    f"""SELECT {name_column} FROM {name_table}
                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}' and success={success}""")
            else:
                self.cur.execute(
                    f"""SELECT {name_column} FROM {name_table}
                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'""")

            # listik = [i[0] for i in self.cur.fetchall()]
            # list_of_data = [datetime.datetime.strftime(i, "%Y-%m-%d %H:%M:%S") for i in listik]
            first_timestamp = [str(i[0].time())[0:-7]
                               for i in self.cur.fetchall()]
            first_timestamp = [str(self.now_date)+' ' +
                               i for i in first_timestamp]
            list_of_data = [datetime.datetime.strptime(
                i, "%Y-%m-%d %H:%M:%S") for i in first_timestamp]

        if list_of_data:
            return sorted(list_of_data)
        else:
            return []

    def data_of_breaks(self, now_date_start, now_date_end) -> dict:
        """
        Формирование словаря по поломкам:
        Ключ - время обнаружение поломки
        Значение - (Имя поломки, Время починки(время или None), -100(оптиональное значение для отсройки графика))
        """

        # Парсинг значений с поломками
        self.cur.execute(f"""SELECT name_break,date_of_create_break,date_of_repair_break from breaks
                    WHERE date_of_create_break<'{now_date_end}' AND (date_of_repair_break>'{now_date_start}' OR date_of_repair_break IS NULL)""")
        correct_timestamp_dict_2 = {}
        # Составление словаря ключ(дата обнаружения поломки):значение(кортеж(название_поломки,дата починки, -100(значение по умолчанию для отображения на графике)))
        correct_timestamp_dict_2 = {
            i[1]: (i[0], i[2], -100) for i in self.cur.fetchall()}
        if correct_timestamp_dict_2:
            return correct_timestamp_dict_2
        else:
            return {}

    def data_of_sorted(self, now_date_start, now_date_end):
        """
        Формирование двух списков по отсортированным (попытка и удачно) категориям
        """

        self.cur.execute(f"""SELECT category_id FROM grab_attempt
                        WHERE attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}'""")
        list_of_category_grab = [i[0] for i in self.cur.fetchall()]
        self.cur.execute(f"""SELECT category_id FROM grab_attempt
                        WHERE attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}' and success={True}""")
        list_of_category_sorted = [i[0] for i in self.cur.fetchall()]
        return list_of_category_grab, list_of_category_sorted

    def get_test_id(self, now_date_start, now_date_end) -> list:
        """
        Выдает список тестов(id) за сегодняшний день
        """
        self.cur.execute(
            f"SELECT test_id FROM grab_attempt WHERE attempt_timestamp>'{now_date_start}' and attempt_timestamp<'{now_date_end}'")
        test_id = [i[0]
                   for i in set(self.cur.fetchall()) if bool(i[0]) == True]
        return test_id

    def get_data_odometr(self, test_id:int, key: str):
        """
            Input:
            - test_id - запрос данных по определенному тесту

            OutPut:

            - x_distributin,
            - y_distribution,
            - z_distribution,
            - distance
        """
        try:
            self.cur.execute(
                f"SELECT {key} FROM odometr_data WHERE test_id='{test_id}'")
        except Exception as e:
            print(f'Ошибка при запросе данных. {e}')
        match key:
            case 'distance':
                output = 0
                for distance in self.cur.fetchall():
                    output += int(distance[0])

                return output
                
            case _:
                output = []
                for data in self.cur.fetchall():
                    data = (data[0][2:-1].split(' '))
                    output.append(data)
                return output


testclass = Executer()

#testclass.get_data_odometr(3032,"y_distribution")