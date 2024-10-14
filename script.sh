#!/bin/bash

username=$(whoami)

echo $username

namepipenv=$(ls /home/$username/.local/share/virtualenvs|grep AutoReport)

echo $namepipenv


cd /home/`whoami`/AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/script_upload_graphs.py
