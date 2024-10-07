#!/bin/bash
source .venv/Scripts/activate || source .venv/bin/activate
cd xdccDownloadManager/
python manage.py collectstatic --noinput
python manage.py watch_static &
python -m uvicorn --workers=4 xdccDownloadManager.asgi:application --reload --reload-include *.html