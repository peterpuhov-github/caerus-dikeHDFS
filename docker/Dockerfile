
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Dockerfile for installing the necessary dependencies for building Hadoop.
# See BUILDING.txt.

#FROM ubuntu:bionic
FROM ubuntu:focal

WORKDIR /root

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

#####
# Disable suggests/recommends
#####
RUN echo APT::Install-Recommends "0"\; > /etc/apt/apt.conf.d/10disableextras
RUN echo APT::Install-Suggests "0"\; >>  /etc/apt/apt.conf.d/10disableextras

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_TERSE true
ENV TZ=US/Eastern

# hadolint ignore=DL3008
RUN apt-get -q update \
    && apt-get -q install -y --no-install-recommends \
        ant \
        apt-utils \
        bats \
        build-essential \
        bzip2 \
        clang \
        cmake \
        curl \
        doxygen \
        findbugs \
        fuse \
        g++ \
        gcc \
        git \
        gnupg-agent \
        libbcprov-java \
        libbz2-dev \
        libcurl4-openssl-dev \
        libfuse-dev \
        libprotobuf-dev \
        libprotoc-dev \
        libsasl2-dev \
        libsnappy-dev \
        libssl-dev \
        libtool \
        libzstd-dev \
        locales \
        make \
        maven \
        openjdk-11-jdk \
        openjdk-8-jdk \
        pinentry-curses \
        pkg-config \
        python \
        python2.7 \
        python-pkg-resources \
        python-setuptools \
        rsync \
        shellcheck \
        software-properties-common \
        sudo \
        valgrind \
        zlib1g-dev \
        ssh \
        pdsh \
        openssh-server \
        net-tools \
        gdb \
        valgrind \
        ca-certificates lsb-release wget \
        tzdata \
        libsnappy-dev liblz4-dev libzstd-dev

# python-pip \
# python-wheel \

#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*
RUN wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb

RUN apt-get -q install -y --no-install-recommends \
    ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb

RUN apt-get -q update \
    && apt-get -q install -y --no-install-recommends \
        libarrow-dev \
        libarrow-glib-dev \
        libarrow-dataset-dev \
        libarrow-flight-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


######
# Set env vars required to build Hadoop
######
ENV MAVEN_HOME /usr
# JAVA_HOME must be set in Maven >= 3.5.0 (MNG-6003)
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV FINDBUGS_HOME /usr

###
# Avoid out of memory errors in builds
###
ENV MAVEN_OPTS -Xms256m -Xmx1536m

RUN mkdir -p /opt/hadoop
ARG HADOOP_VERSION
ENV ENV_HADOOP_VERSION=$HADOOP_VERSION

RUN mkdir -p /opt/hadoop
RUN curl -L https://downloads.apache.org/hadoop/common/hadoop-${ENV_HADOOP_VERSION}/hadoop-${ENV_HADOOP_VERSION}.tar.gz | tar -xz -C /opt/hadoop


RUN mkdir -p /opt/orc
#RUN curl -L https://downloads.apache.org/orc/orc-1.6.9/orc-1.6.9.tar.gz | tar -xz -C /opt/orc
RUN curl -L https://downloads.apache.org/orc/orc-1.6.10/orc-1.6.10.tar.gz | tar -xz -C /opt/orc \
    && cd /opt/orc/orc-1.6.10 \
    && mkdir build \
    && cd build \
    && cmake .. -DBUILD_JAVA=OFF \
    && make package \
    && make install

COPY entry.sh /usr/local/bin/entry.sh
RUN chmod a+x /usr/local/bin/entry.sh

ENTRYPOINT ["/usr/local/bin/entry.sh"]
