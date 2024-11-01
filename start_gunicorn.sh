#!/bin/sh

# For this to work, the tigercart_env virtual environment must be set up:
#   python3 -m venv tigercart_env
#   . tigercart_env/bin/activate
#   python3 -m pip install -r requirements.txt

cd /home/app/tigercart
. tigercart_env/bin/activate
gunicorn --bind 127.0.0.1:8000 app:app --workers 5
