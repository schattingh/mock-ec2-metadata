FROM alpine:latest

RUN apk add --no-cache python3

RUN pip3 install boto3 flask gunicorn PyYAML

WORKDIR /app
