#!/bin/bash

username=$(whoami)

namepipenv=$(ls /home/$username/.local/share/virtualenvs|grep AutoReport)


cd ../AutoReport &&/home/`whoami`/.local/share/virtualenvs/$namepipenv/bin/python3 /home/`whoami`/AutoReport/make_actual_graph.py
