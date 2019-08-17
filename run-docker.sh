#!/bin/bash

DIR=$(pwd)
DIRNAME=$(basename ${DIR})

function_dev () {
  echo 'Running docker container with Flask in development mode'
  docker run -it --rm \
  -p 5000:5000 \
  -v ~/.aws:/root/.aws \
  -v $DIR:/app \
  -e FLASK_APP=default.py \
  -e FLASK_ENV=development \
  ${DIRNAME} flask run --host=0.0.0.0
  #  -p 169.254.169.254:80:5000 \
}

function_prd () {
  echo 'Running docker container with Flask and Gunicorn'
  docker run -it --rm \
  -p 5000:5000 \
  -v ~/.aws:/root/.aws \
  -v $DIR:/app \
  -e FLASK_APP=default.py \
  ${DIRNAME} gunicorn -b :5000 default:app
}

function_it () {
  echo 'Running docker container interactively'
  docker run -it --rm \
  -v ~/.aws:/root/.aws \
  -v $DIR:/app \
  ${DIRNAME} /bin/ash
}

case $1 in

  'dev')
  function_dev
  ;;

  'prd')
  function_prd
  ;;

  'it')
  function_it
  ;;

  *)
  echo "Please give me a command line argument of either dev or prd else I don't know what to do"
  ;;

esac
