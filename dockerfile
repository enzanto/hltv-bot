FROM python:3.7-buster


RUN apt-get update && apt-get install cron -y
RUN cp /usr/share/zoneinfo/Europe/Oslo /etc/localtime
RUN python -m pip install --upgrade pip
COPY . .
RUN pip3 install -r requirements.txt
RUN cp crontab /etc/crontab


CMD ["cron", "-f"]