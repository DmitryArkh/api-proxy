FROM python:3.12-alpine

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app

LABEL maintainer="DmitryArkh <contact@dmitryarkh.me>"
ENTRYPOINT python ./app.py
EXPOSE 5000