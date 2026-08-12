@echo off

set FLASK_APP=main.py
set PYTHONDONTWRITEBYTECODE=1

uv run main.py
