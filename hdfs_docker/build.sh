#!/usr/bin/env bash

set -e               # exit on error
pushd "$(dirname "$0")" # connect to root

ROOT_DIR=$(pwd)

DOCKER_DIR=${ROOT_DIR}
DOCKER_FILE="${DOCKER_DIR}/Dockerfile"
DOCKER_NAME=hdfs_server

DOCKER_CMD="docker build -t ${DOCKER_NAME} --build-arg HADOOP_VERSION -f $DOCKER_FILE $DOCKER_DIR"
eval "$DOCKER_CMD"
popd
