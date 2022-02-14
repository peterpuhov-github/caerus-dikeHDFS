#!/usr/bin/env bash

set -e               # exit on error
pushd "$(dirname "$0")" # connect to root

ROOT_DIR=$(pwd)

DOCKER_DIR=${ROOT_DIR}
DOCKER_FILE="${DOCKER_DIR}/Dockerfile"
DOCKER_NAME=hdfs_server

DOCKER_CMD="docker build -t ${DOCKER_NAME} --build-arg HADOOP_VERSION -f $DOCKER_FILE $DOCKER_DIR"
eval "$DOCKER_CMD"

USER_NAME=${SUDO_USER:=$USER}
USER_ID=$(id -u "${USER_NAME}")
GROUP_ID=$(id -g "${USER_NAME}")

# Set the home directory in the Docker container.
DOCKER_HOME_DIR=${DOCKER_HOME_DIR:-/home/${USER_NAME}}

docker build -t "${DOCKER_NAME}-${USER_NAME}" - <<UserSpecificDocker
FROM ${DOCKER_NAME}
RUN rm -f /var/log/faillog /var/log/lastlog
RUN groupadd --non-unique -g ${GROUP_ID} ${USER_NAME}
RUN useradd -g ${GROUP_ID} -u ${USER_ID} -k /root -m ${USER_NAME} -d "${DOCKER_HOME_DIR}"
RUN echo "${USER_NAME} ALL=NOPASSWD: ALL" >> "/etc/sudoers"
ENV HOME "${DOCKER_HOME_DIR}"

USER ${USER_NAME}
WORKDIR "${DOCKER_HOME_DIR}"
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
RUN cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
RUN chmod 0600 ~/.ssh/authorized_keys
UserSpecificDocker

popd
