#!/bin/bash

if [ -n "$1" ]
then
if [ -n "$2" ]
then
cd ../AutoReport && python3 script_upload_graphs.py $1 $2
else
cd ../AutoReport && python3 script_upload_graphs.py $1 
fi
else cd ../AutoReport && python3 script_upload_graphs.py
fi
