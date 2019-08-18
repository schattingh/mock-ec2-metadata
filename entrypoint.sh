#!/bin/sh

function_dev() {
  /usr/bin/flask run --host=0.0.0.0
}

function_prd() {
  /usr/bin/gunicorn --bind=:5000 \
  --workers=2 \
  --threads=4 \
  --worker-class=gthread \
  --worker-tmp-dir /dev/shm \
  --log-file=- \
  --access-logfile=- \
  default:app
}

case ${ENVIRONMENT} in
  'dev')
  function_dev
  ;;

  'prd')
  function_prd
  ;;

  *)
  echo "You haven't sent an appropriate Environment;  I don't know what to do"
  exit 1
  ;;

esac
