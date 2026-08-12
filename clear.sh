#! /bin/bash

rm -rf ./migrations
rm -rf app.db

uv run flask db init
uv run flask db migrate
uv run flask db upgrade