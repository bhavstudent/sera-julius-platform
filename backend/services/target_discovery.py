# backend/services/target_discovery.py
import requests
import random
from typing import List, Dict

class GlobalTargetDiscovery:
    def __init__(self):
        self.public_ntp_servers = self._load_public_ntp_servers()
        
    def _load_public_ntp_servers(self) -> List[str]:
        """Load public NTP servers from various sources"""
        sources = [
            "https://www.pool.ntp.org/servers.json",
            "https://ntp.org/servers.json"
        ]
        servers = []
        for url in sources:
            try:
                resp = requests.get(url, timeout=10)
                data = resp.json()
                servers.extend([s["hostname"] for s in data["servers"]])
            except:
                continue
        return servers
        
    async def discover_targets(self, limit: int = 1000) -> List[Dict]:
        """Discover new NTP servers to scan"""
        targets = []
        for _ in range(limit):
            server = random.choice(self.public_ntp_servers)
            targets.append({
                "hostname": server,
                "type": "public_ntp",
                "score": random.random()
            })
        return targets
