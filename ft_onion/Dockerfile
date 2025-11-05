FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    tor \
    nginx \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

COPY config/nginx.conf /etc/nginx
COPY config/torrc /etc/tor/torrc
COPY config/ssh/sshd_config /etc/ssh/sshd_config
COPY www/index.html /var/www/html/index.html

COPY config/authorized_keys /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

COPY tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 4242

ENTRYPOINT [ "/tools/entrypoint.sh" ]