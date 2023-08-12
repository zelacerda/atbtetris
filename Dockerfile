FROM alpine:3.17

ENV TERM xterm-256color

RUN apk update \
    && apk add python3

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./*.py ./

CMD ["python3", "main.py"]