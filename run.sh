#! /bin/bash

export FLASK_APP=main.py
export PYTHONDONTWRITEBYTECODE=1

uv run main.py
