#! /bin/bash

export FLASK_APP=main.py
export PYTHONDONTWRITEBYTECODE=1

export MAIL_SERVER='smtp.gmail.com'
export MAIL_PORT=587
export MAIL_USE_TLS=1
# export MAIL_USERNAME=''
# export MAIL_PASSWORD=''

./main.py
