# backend/security/measures.py
import hashlib
import secrets
import time
from typing import Dict

class SecurityMeasures:
    def __init__(self):
        self.throttle_intervals = {}  # Per-target throttling
        self.rate_limits = {}         # Per-IP rate limits
        
    def generate_unique_id(self) -> str:
        """Generate unique node ID with cryptographic strength"""
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    
    def throttle(self, target: str, duration: int = 60) -> bool:
        """Implement target throttling to prevent flooding"""
        now = time.time()
        if target in self.throttle_intervals:
            last = self.throttle_intervals[target]
            if now - last < duration:
                return False
        self.throttle_intervals[target] = now
        return True
    
    def check_rate_limit(self, ip: str, max_requests: int = 10) -> bool:
        """Check IP rate limit"""
        if ip not in self.rate_limits:
            self.rate_limits[ip] = {"count": 0, "reset": time.time() + 3600}
        
        now = time.time()
        if now > self.rate_limits[ip]["reset"]:
            self.rate_limits[ip]["count"] = 0
            self.rate_limits[ip]["reset"] = now + 3600
        
        if self.rate_limits[ip]["count"] >= max_requests:
            return False
            
        self.rate_limits[ip]["count"] += 1
        return True