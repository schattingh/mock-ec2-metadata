FROM alpine:latest

RUN apk add --no-cache python3 tini

RUN pip3 install boto3 flask gunicorn PyYAML

WORKDIR /app

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "/sbin/tini", "--", "/app/entrypoint.sh" ]
