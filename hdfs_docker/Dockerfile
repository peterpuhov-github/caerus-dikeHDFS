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

# Install Hadoop dependencies
RUN apt-get -q update \
    && apt-get -q install -y --no-install-recommends \
    openjdk-8-jdk \
    net-tools \
    curl \
    netcat

RUN mkdir -p /opt/hadoop
ENV ENV_HADOOP_VERSION=3.3.0
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

RUN mkdir -p /opt/hadoop
RUN curl -L https://downloads.apache.org/hadoop/common/hadoop-${ENV_HADOOP_VERSION}/hadoop-${ENV_HADOOP_VERSION}.tar.gz | tar -xz -C /opt/hadoop

COPY entry.sh /usr/local/bin/entry.sh
RUN chmod a+x /usr/local/bin/entry.sh

ENTRYPOINT ["/usr/local/bin/entry.sh"]
