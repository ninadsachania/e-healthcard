#! /bin/bash

export FLASK_APP=main.py
export PYTHONDONTWRITEBYTECODE=1

export MAIL_SERVER='smtp.gmail.com'
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=pbtemp.xyz@gmail.com
export MAIL_PASSWORD=PBtemp@123

chmod u+x ./main.py
./main.py
