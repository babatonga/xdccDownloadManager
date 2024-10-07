FROM python:3

# Set the working directory in the container
WORKDIR /app

# Install npm
RUN apt-get update && apt-get install -y npm

# Install yuglify
RUN npm install -g yuglify

# Copy files
COPY xdccDownloadManager/ /app/xdccDownloadManager/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY manage.py /app/manage.py
COPY requirements.txt /app/requirements.txt

# prepare static mount
RUN mkdir -p /app/mnt/
RUN mkdir -p /app/logs/

# prepare entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]