FROM python:3.13-alpine

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

LABEL maintainer="DmitryArkh <contact@dmitryarkh.me>"
CMD ["python", "app.py"]
EXPOSE 5050
