#!/bin/bash

DIR=$(pwd)
DIRNAME=$(basename ${DIR})

docker build . -t ${DIRNAME}
