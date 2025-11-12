FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    iproute2 \
    tcpdump \
    ftp \
    vsftpd \
    python3 \
    python3-pip \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install scapy

WORKDIR /app

