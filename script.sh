#!/bin/bash/env python3

if [ -n "$1" ]
then
if [ -n "$2" ]
then
python3 script_upload_graphs.py $1 $2
else
python3 script_upload_graphs.py $1 
fi
else python3 script_upload_graphs.py
fi
