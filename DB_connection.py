import psycopg2
import yaml

with open('config.yaml') as f:
            dataframe = yaml.load(f,yaml.FullLoader)

def make_connection():
    """
    Возвращает указатели для работы с бд

    Output:
    conn(connection),cur(cursor)
    """


    conn = psycopg2.connect(dbname = dataframe['dbname'],
        user=dataframe['user'],
        password=dataframe['password'],
        host=dataframe['host'],
        port=dataframe['port']
    )
    cur = conn.cursor()
    return conn,cur
