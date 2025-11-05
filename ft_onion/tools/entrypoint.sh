#!/bin/bash

set -e 

echo "Starting Tor..."
tor -f /etc/tor/torrc &

echo "Waiting for .onion address..."
while [ ! -f /var/lib/tor/hidden_service/hostname ]; do
    sleep 1
done

echo "Your .onion address:"
cat /var/lib/tor/hidden_service/hostname

echo "Starting SSH..."
/usr/sbin/sshd

echo "Starting Nginx..."
nginx -g 'daemon off;'