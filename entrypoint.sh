#!/bin/bash
set -e

# Workdir
WORKDIR=/app
cd $WORKDIR

# check if environment variables are set
if [ -z "$SECRET_KEY" ]; then
    echo "SECRET_KEY is not set"
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "ALLOWED_HOSTS is not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL is not set"
    exit 1
fi

# start time measurement
start=$(date +%s)

# Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# set environment variables
export DJANGO_SETTINGS_MODULE=xdccDownloadManager.settings
export PYTHONPATH=$WORKDIR:$PYTHONPATH

# copy static files
mkdir -p $WORKDIR/mnt/static
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations
python manage.py makemigrations "irc_xdcc_manager"
python manage.py migrate

# Clear Cache
python manage.py clearcache

# end time measurement
end=$(date +%s)
runtime=$((end-start))
echo "Build Runtime: $runtime seconds"

# Run background tasks
#python manage.py listen &
#python manage.py runapscheduler &

# Run gunicorn django server
python -m gunicorn xdccDownloadManager.asgi:application -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --log-level=info