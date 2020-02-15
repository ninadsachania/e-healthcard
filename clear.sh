#! /bin/bash

rm -rf ./migrations
rm -rf app.db

flask db init
flask db migrate
flask db upgrade