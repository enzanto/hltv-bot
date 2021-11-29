FROM python:3.7-buster

COPY . .
RUN apt-get update && apt-get install cron -y
RUN cp /usr/share/zoneinfo/Europe/Oslo /etc/localtime
RUN cp crontab /etc/crontab
RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt


CMD ["cron", "-f"]