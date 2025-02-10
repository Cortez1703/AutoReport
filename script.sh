#!/bin/bash

username=$(whoami)

namepipenv=$(ls /home/$username/.local/share/virtualenvs|grep AutoReport)


if [ -n "$1" ]
then
if [ -n "$2" ]
then
cd ../AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/upload_graphs.py $1 $2
else
cd ../AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/upload_graphs.py $1 
fi
else cd /home/`whoami`/AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/upload_graphs.py
fi
