#!/bin/bash

# python3 manage.py dbshell < ./data_db.sql
python3 manage.py migrate
python3 manage.py makemigrations
python3 manage.py migrate

