#!/bin/bash

username=$(whoami)

namepipenv=$(ls /home/$username/.local/share/virtualenvs|grep AutoReport)

chat_id=872965519

echo $chat_id

if [ -n "$1" ]
then
echo $1
cd /home/`whoami`/AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/script_upload_graphs.py $1
else cd /home/`whoami`/AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/script_upload_graphs.py
fi
