# Репозиторий, созданный для автоматической отчетности тестирования робота за сутки
## Установка и запуск напрямую
- Скачать репозиторий по пути /home/*user*. Т.е. в корневую папку для юзера
- Перейти в папку проекта `cd /home/*user*/AutoReport`
- Создать файл setting.py со данными по подключениям (будет представлено ниже)
- Активировать виртуальное окружение `pipenv shell`
- Выполнить команду `pip install -r requirements.txt`
- Запустить скрипт `bash script.sh`
## Установка и настройка автоматической выгрузкой через crontab
- Скачать репозиторий по пути /home/*user*. Т.е. в корневую папку для юзера
- Перейти в папку проекта `cd /home/*user*/AutoReport`
- Создать файл setting.py со данными по подключениям (будет представлено ниже)
- Активировать виртуальное окружение 'pipenv shell'
- Выполнить команду `pip install -r requirements.txt`
- Зайти в cron командой `crontab -e`(выбрать '1') и ввести в самом конце файла следующую строку: `00 21 * * * bash /home/cortez/AutoReport/script.sh`
- `Ctrl+O`,`Enter`,`Ctrl+X`
## Файл setting.py

class config():   

     def __init__(self):
           self.DB_CONFIG={
             'dbname': *DBNAME*,
    'user': *USER*,
    'password': *PASSWORD*,
    'host': *IP_ADRESS*,
    'port': *PORT*
}

        self.id_my=*USER_ID*
        self.group_id=*GROUP_ID*
        self.api_token_bot=*API_BOT_TOKEN*
