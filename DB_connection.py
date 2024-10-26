import psycopg2
from setting import config

settings = config()
def make_connection():
    conn = psycopg2.connect(dbname = settings.DB_CONFIG['dbname'],
        user=settings.DB_CONFIG['user'],
        password=settings.DB_CONFIG['password'],
        host=settings.DB_CONFIG['host'],
        port=settings.DB_CONFIG['port']
    )
    cur = conn.cursor()
    return conn,cur