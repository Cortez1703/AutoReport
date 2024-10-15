# Репозиторий, созданный для автоматической отчетности тестирования робота за сутки
##Первоначальная настройка
- Скачать репозиторий на домашнюю страницу пользователя.(`/home/*user*`)
- Перейти в папку проекта `cd /home/*user*/AutoReport`
- Создать файл setting.py с данными по подключениям (будет представлено ниже)
- Активировать виртуальное окружение `pipenv shell`
- Выполнить команду `pip install -r requirements.txt`
- Выйти из виртуального окружения командой `$exit`
## Запуск напрямую
- Перейти в папку проекта `cd /home/*user*/AutoReport`
- Активировать виртуальное окружение `pipenv shell`
- Запустить скрипт `bash script.sh`

По окончании выполнения скрипта в папке *AutoReport* появится папка Reports, в которой будут сохранены pdf-файлы со всеми графиками.
## Настройка автоматической выгрузкой через crontab
- Зайти в cron командой `crontab -e`(выбрать 1) и ввести в самом конце файла следующую строку: `00 21 * * * bash /home/*username*/*AutoReport/script.sh` (Вместо *username* ввести имя пользователя, через которого настраиваете(Узнать можно командой whoami))
- `Ctrl+O`,`Enter`,`Ctrl+X`

Этот скрипт будет выгружать имеющиеся за нынешнюю дату графики каждый день в 21-00 по текущему времени
## Файл setting.py

```python
class config():   
      def __init__(self):
            self.DB_CONFIG={
             'dbname': *DBNAME*,
              'user': *USER*,
              'password': *PASSWORD*,
              'host': *IP_ADRESS*,
              'port': *PORT*}
            self.id_my=*USER_ID*
            self.group_id=*GROUP_ID*
            self.api_token_bot=*API_BOT_TOKEN*
