FROM nginx:alpine
LABEL maintainer="DmitryArkh <contact@dmitryarkh.me>"

RUN apk add --no-cache python3 py3-pip py3-yaml

WORKDIR /app
COPY . /app

CMD ["sh", "-c", "python3 /app/main.py & nginx -g 'daemon off;'"]

EXPOSE 5050
