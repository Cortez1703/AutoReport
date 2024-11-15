from DB_connection import make_connection

conn,cur = make_connection()
def get_breaks(cursor):
    cursor.execute("""SELECT * FROM breaks WHERE date_of_repair_break IS NULL""")
    data = cursor.fetchall()
    if data:
        list_of_repair = [str(i[1])+'---'+ str(i[2]) for i in data]
    else:
        list_of_repair = []
    return list_of_repair

def get_ans(list_of_breaks:list):
    ans = ''
    if list_of_breaks:
        ans+= 'Не решены следующие проблемы:\n'
        for i in list_of_breaks:
            ans+=f'{i}\n'
    return ans