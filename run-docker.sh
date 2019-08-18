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
  -e ENVIRONMENT=dev \
  ${DIRNAME}
}

function_prd () {
  echo 'Running docker container with Flask and Gunicorn'
  docker run -d --rm \
  -p 5000:5000 \
  -v ~/.aws:/root/.aws \
  -e FLASK_APP=default.py \
  -e ENVIRONMENT=prd \
  ${DIRNAME}
}

function_it () {
  echo 'Running docker container interactively'
  docker run -it --rm \
  --entrypoint=/bin/ash \
  ${DIRNAME}
  # -v ~/.aws:/root/.aws \
  # -v $DIR:/app \

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
