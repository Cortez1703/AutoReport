from Logic.DB_connection import make_connection
import datetime
import numpy as np

connection, cursor = make_connection()


class Executer:

    def __init__(self, cur=cursor, con=connection):
        self.cur = cur
        self.con = con
        self.now_date = datetime.date.today()

    def axis_standart_graph(self,
                            name_table: str,
                            name_column: str,
                            date_start: str,
                            date_end: str,
                            ID: int | None = None,
                            success: bool | None = None) -> np.array:
        """
        Формирование осей х,y для обычного графика

        Optional:
            ID - если не указан - данные за весь день
            success - если указан - массивы для успешных захватом.

        Output:
            timeArray - axis X
            grabArray - axis Y
        """

        # Формирование по ID
        match ID:
            case int():
                match success:
                    case bool():
                        self.cur.execute(
                            f"""SELECT {name_column} FROM {name_table}
                                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'
                                AND test_id={ID} and success={success}""")

                    case _:
                        self.cur.execute(
                            f"""SELECT {name_column} FROM {name_table}
                                    WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'
                                    AND test_id={ID} """)

            case _:
                match success:
                    case bool():
                        self.cur.execute(
                            f"""SELECT {name_column} FROM {name_table}
                                WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'
                                AND success={success}""")

                    case _:
                        self.cur.execute(
                            f"""SELECT {name_column} FROM {name_table}
                                    WHERE {name_column}>'{date_start}' AND {name_column}<'{date_end}'
                                    """)

        timeArray = sorted([i[0] for i in self.cur.fetchall()])
        grabArray = np.arange(0, len(timeArray))
        return timeArray, grabArray

    def data_of_breaks(self, now_date_start, now_date_end) -> dict:
        """
        Формирование словаря по поломкам:
        Ключ - время обнаружение поломки
        Значение - (Имя поломки, Время починки(время или None), -100(оптиональное значение для отсройки графика))
        """

        # Парсинг значений с поломками
        self.cur.execute(f"""SELECT name_break,date_of_create_break,date_of_repair_break FROM breaks
                    WHERE date_of_create_break<'{now_date_end}'
                    AND (date_of_repair_break>'{now_date_start}' OR date_of_repair_break IS NULL)""")
        return [i for i in self.cur.fetchall()]

    def axis_bar_graph(self, now_date_start, now_date_end):
        """
        Возвращает 2 словаря с фракциями.

        dict_grab - словарь попыток захвата key[фракция]:value[количество]
        dict_sorted - словарь успешных попыток захвата key[фракция]:value[количество]
        """

        self.cur.execute(f"""SELECT category_id FROM grab_attempt
                        WHERE attempt_timestamp>'{now_date_start}'
                        AND attempt_timestamp<'{now_date_end}'""")

        # Распаковываем запрос из SQL.
        list_of_category_grab = [i[0] for i in self.cur.fetchall()]

        # Формируем словарь фракция:сколько раз встречалась
        dict_grab = {i: [list_of_category_grab.count(
            i)] for i in set(list_of_category_grab)}

        self.cur.execute(f"""SELECT category_id FROM grab_attempt
                        WHERE attempt_timestamp>'{now_date_start}'
                        AND attempt_timestamp<'{now_date_end}' and success={True}""")

        # Распаковываем запрос из SQL.
        list_of_category_sorted = [i[0] for i in self.cur.fetchall()]

        # Формируем словарь фракция:сколько раз встречалась
        dict_sorted = {i: [list_of_category_sorted.count(
            i)] for i in set(list_of_category_sorted)}

        for i in dict_grab:
            if i in dict_sorted:
                pass
            else:
                dict_sorted[i] = [0]

        return dict_grab, dict_sorted

    def get_test_id(self, now_date_start, now_date_end) -> list:
        """
        Выдает список тестов(id) за сегодняшний день
        """
        self.cur.execute(
            f"""SELECT test_id FROM grab_attempt
            WHERE attempt_timestamp>'{now_date_start}'
            AND attempt_timestamp<'{now_date_end}'""")

        # Условный костыль,т.к. выдает почему-то иногда пустой кортеж
        test_id = [i[0]
                   for i in set(self.cur.fetchall()) if bool(i[0]) == True]
        return test_id

    def get_data_odometr(self, test_id: int, key: str):
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
