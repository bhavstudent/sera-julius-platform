import threading
from typing import List, Dict
from scapy.all import sniff, IP, UDP, NTP

class NTPMonitor:
    def __init__(self):
        self.anomalies = []
        self.lock = threading.Lock()
        self.running = False

    def start_monitoring(self, network_scope: str, timeout: int = 10):
        """Start capturing NTP packets for a given time."""
        self.running = True
        self.anomalies = []

        def packet_handler(pkt):
            if self.running and pkt.haslayer(NTP) and pkt.haslayer(IP):
                self.analyze_ntp_packet(pkt)

        sniff(filter="udp port 123", prn=packet_handler, store=0, timeout=timeout)
        self.running = False
        return self.anomalies

    def analyze_ntp_packet(self, pkt):
        """Analyze NTP packet for anomalies."""
        with self.lock:
            # Simple check: Stratum 0 (kiss-of-death) or suspicious stratum
            ntp = pkt[NTP]
            if ntp.stratum == 0 or ntp.stratum > 15:
                self.anomalies.append({
                    "ip": pkt[IP].src,
                    "severity": "HIGH",
                    "variation": "Stratum {} detected".format(ntp.stratum)
                })
            # You can add more heuristics here (timing, version, etc.)
