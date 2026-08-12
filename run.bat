@echo off

set FLASK_APP=main.py
set PYTHONDONTWRITEBYTECODE=1

set MAIL_SERVER=smtp.gmail.com
set MAIL_PORT=587
set MAIL_USE_TLS=1
set MAIL_USERNAME=pbtemp.xyz@gmail.com
set MAIL_PASSWORD=PBtemp@123

uv run main.py
