import threading
from typing import List, Dict
from scapy.all import sniff, ARP

class ARPMonitor:
    def __init__(self):
        self.attacks = []
        self.lock = threading.Lock()
        self.running = False
        self.seen_macs = {}

    def start_monitoring(self, network_scope: str, timeout: int = 10):
        """Start capturing ARP packets for a given time."""
        self.running = True
        self.attacks = []
        self.seen_macs = {}

        def packet_handler(pkt):
            if self.running and pkt.haslayer(ARP) and pkt[ARP].op == 2:  # ARP reply
                self.analyze_arp_packet(pkt)

        sniff(filter="arp", prn=packet_handler, store=0, timeout=timeout)
        self.running = False
        return self.attacks

    def analyze_arp_packet(self, pkt):
        """Analyze ARP packet for spoofing."""
        with self.lock:
            ip = pkt[ARP].psrc
            mac = pkt[ARP].hwsrc

            # If we've seen this IP with a different MAC before → possible spoof
            if ip in self.seen_macs and self.seen_macs[ip] != mac:
                self.attacks.append({
                    "ip": ip,
                    "spoofed_mac": mac,
                    "severity": "HIGH"
                })
            else:
                self.seen_macs[ip] = mac
