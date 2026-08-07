#!/usr/bin/env python3
"""
packet_sniffer.py - Packet sniffer with crypto address detection
MERGED FROM JULIUS → SERA PLATFORM
Integration with Sera authentication, audit, and database
"""

import re
import json
import logging
import threading
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

# Sera-specific imports (with fallbacks)
try:
    from scapy.all import sniff, IP, TCP, UDP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("WARNING: Scapy not installed. Install with: pip install scapy")

# Sera configuration
try:
    from config import settings
    SERA_CONFIG = settings
except ImportError:
    SERA_CONFIG = None
    print("WARNING: Sera config not found. Using defaults.")

# Setup Sera logging
LOG_DIR = SERA_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'sera_packet_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_packet_monitor")

# Crypto address patterns (from Julius - ENHANCED for Sera)
PATTERNS = {
    "Bitcoin": r"1[1-9A-HJ-NP-Za-km-z]{25,34}|3[1-9A-HJ-NP-Za-km-z]{25,34}|bc1[a-z0-9]{39,59}",
    "Ethereum": r"0x[a-fA-F0-9]{40}",
    "Monero": r"4[1-9A-HJ-NP-Za-km-z]{94}",
    "Litecoin": r"[LM][1-9A-HJ-NP-Za-km-z]{26,33}",
    "Dogecoin": r"D[1-9A-HJ-NP-Za-km-z]{33}",
    # Sera-specific patterns
    "USDT_ERC20": r"0x[a-fA-F0-9]{40}",
    "USDT_TRC20": r"T[1-9A-HJ-NP-Za-km-z]{33}",
    "Phone": r"\+?[1-9]\d{1,14}",
    "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IP": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "API_Key": r"[a-zA-Z0-9]{32,64}",
    "JWT": r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
}

class SeraPacketSniffer:
    """Packet sniffer with Sera integration"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.is_running = False
        self.sniffer_thread = None
        self.detections = []
        self.packet_count = 0
        
        # Sera-specific components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        self.alerts = self._init_alerts()
        
        # Configuration
        self.interface = self.config.get('interface', 'eth0')
        self.max_packets = self.config.get('max_packets', 0)
        self.timeout = self.config.get('timeout', None)
        self.store_packets = self.config.get('store_packets', True)
        self.alert_on_detection = self.config.get('alert_on_detection', True)
        
        logger.info("Sera Packet Sniffer initialized")
    
    def _init_database(self):
        """Initialize Sera database connection"""
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
    
    def _init_alerts(self):
        """Initialize Sera alert system"""
        try:
            from services.alert_service import trigger_alert
            return trigger_alert
        except ImportError:
            logger.warning("Alert service not available - using local alerts")
            return None
    
    def detect_crypto(self, packet):
        """Detect crypto addresses and sensitive data in packets"""
        if not SCAPY_AVAILABLE or not self.is_running:
            return
            
        try:
            # Check for IP layer
            if not packet.haslayer(IP):
                return
            
            # Get payload based on protocol
            payload = None
            if packet.haslayer(TCP):
                payload = bytes(packet[TCP].payload)
            elif packet.haslayer(UDP):
                payload = bytes(packet[UDP].payload)
            else:
                return
            
            # Decode payload
            try:
                payload_str = payload.decode('utf-8', errors='ignore')
            except:
                return
            
            # Check for patterns
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            for name, pattern in PATTERNS.items():
                matches = re.findall(pattern, payload_str)
                for match in matches:
                    # Create detection record
                    detection = {
                        "type": name,
                        "value": match,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "timestamp": datetime.now().isoformat(),
                        "protocol": packet[IP].proto,
                        "packet_id": self.packet_count,
                        "source": "packet_sniffer"
                    }
                    
                    # Store detection
                    self.detections.append(detection)
                    
                    # Log to Sera audit
                    self._log_detection(detection)
                    
                    # Store in Sera database
                    self._store_detection(detection)
                    
                    # Trigger Sera alert
                    if self.alert_on_detection:
                        self._trigger_alert(detection)
                    
                    # Log to console (like Julius)
                    msg = f"[{name}] {match} | {src_ip} -> {dst_ip}"
                    logger.info(msg)
                    print(f"[+] {msg}")
                    
                    # Julius-style transaction logging
                    self._log_transaction(msg)
                    
        except Exception as e:
            logger.error(f"Error in detect_crypto: {e}")
    
    def _log_detection(self, detection: Dict[str, Any]):
        """Log detection to Sera audit system"""
        try:
            if self.audit:
                self.audit(
                    action="crypto_detected",
                    target=detection.get("src_ip"),
                    details=detection
                )
            else:
                # Local fallback
                audit_file = LOG_DIR / f"detections_{datetime.now().strftime('%Y%m%d')}.log"
                with open(audit_file, 'a') as f:
                    f.write(json.dumps(detection) + '\n')
        except Exception as e:
            logger.error(f"Error logging detection: {e}")
    
    def _log_transaction(self, message: str):
        """Julius-style transaction logging"""
        try:
            tx_file = LOG_DIR / "transactions.log"
            with open(tx_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {message}\n")
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")
    
    def _store_detection(self, detection: Dict[str, Any]):
        """Store detection in Sera database"""
        try:
            if self.db:
                # Assuming Sera has a detections table
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO detections (
                        type, value, src_ip, dst_ip, timestamp, 
                        protocol, packet_id, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    detection['type'],
                    detection['value'],
                    detection['src_ip'],
                    detection['dst_ip'],
                    detection['timestamp'],
                    detection['protocol'],
                    detection['packet_id'],
                    detection['source']
                ))
                self.db.commit()
        except Exception as e:
            logger.error(f"Error storing detection: {e}")
    
    def _trigger_alert(self, detection: Dict[str, Any]):
        """Trigger alert in Sera system"""
        try:
            alert_data = {
                "level": "HIGH" if detection['type'] in ["Bitcoin", "Ethereum", "Monero"] else "MEDIUM",
                "type": "crypto_detection",
                "message": f"Crypto address detected: {detection['type']}",
                "details": detection,
                "timestamp": detection['timestamp']
            }
            
            if self.alerts:
                self.alerts(alert_data)
            else:
                # Local alert
                alert_file = LOG_DIR / "alerts.json"
                with open(alert_file, 'a') as f:
                    f.write(json.dumps(alert_data) + '\n')
                
                logger.warning(f"ALERT: {alert_data['message']}")
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    def start_sniffing(self, interface: Optional[str] = None, 
                       timeout: Optional[int] = None):
        """Start packet sniffing"""
        if not SCAPY_AVAILABLE:
            logger.error("Scapy not available - cannot sniff")
            return False
        
        if self.is_running:
            logger.warning("Sniffer already running")
            return False
        
        interface = interface or self.interface
        timeout = timeout or self.timeout
        
        try:
            logger.info(f"Starting packet sniffer on {interface}")
            self.is_running = True
            
            # Start sniffing in background thread
            self.sniffer_thread = threading.Thread(
                target=self._sniff_loop,
                args=(interface, timeout),
                daemon=True
            )
            self.sniffer_thread.start()
            
            logger.info(f"Packet sniffer started on {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting sniffer: {e}")
            self.is_running = False
            return False
    
    def _sniff_loop(self, interface: str, timeout: Optional[int]):
        """Internal sniffing loop"""
        try:
            sniff(
                iface=interface,
                prn=self.detect_crypto,
                store=self.store_packets,
                timeout=timeout
            )
            self.is_running = False
            logger.info("Packet sniffing stopped")
        except Exception as e:
            logger.error(f"Sniffing error: {e}")
            self.is_running = False
    
    def stop_sniffing(self):
        """Stop packet sniffing"""
        if not self.is_running:
            logger.warning("Sniffer not running")
            return
        
        try:
            self.is_running = False
            if self.sniffer_thread and self.sniffer_thread.is_alive():
                self.sniffer_thread.join(timeout=2)
            logger.info("Packet sniffer stopped")
        except Exception as e:
            logger.error(f"Error stopping sniffer: {e}")
    
    def get_detections(self, limit: int = 100) -> List[Dict]:
        """Get recent detections"""
        return self.detections[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sniffer statistics"""
        return {
            "is_running": self.is_running,
            "packet_count": self.packet_count,
            "total_detections": len(self.detections),
            "interface": self.interface,
            "patterns": list(PATTERNS.keys())
        }
    
    def clear_detections(self):
        """Clear detection history"""
        self.detections.clear()
        logger.info("Detection history cleared")

# Singleton for Sera
_sniffer_instance = None

def get_sniffer() -> SeraPacketSniffer:
    """Get or create sniffer instance"""
    global _sniffer_instance
    if _sniffer_instance is None:
        _sniffer_instance = SeraPacketSniffer()
    return _sniffer_instance

# Sera API Endpoint Integration
def start_packet_monitor(interface: str = "eth0") -> Dict[str, Any]:
    """API endpoint: Start packet monitoring"""
    sniffer = get_sniffer()
    if sniffer.start_sniffing(interface):
        return {"status": "success", "message": f"Monitoring started on {interface}"}
    return {"status": "error", "message": "Failed to start monitoring"}

def stop_packet_monitor() -> Dict[str, Any]:
    """API endpoint: Stop packet monitoring"""
    sniffer = get_sniffer()
    sniffer.stop_sniffing()
    return {"status": "success", "message": "Monitoring stopped"}

def get_packet_stats() -> Dict[str, Any]:
    """API endpoint: Get monitoring stats"""
    sniffer = get_sniffer()
    return {"status": "success", "data": sniffer.get_stats()}

def get_packet_detections(limit: int = 100) -> Dict[str, Any]:
    """API endpoint: Get detections"""
    sniffer = get_sniffer()
    detections = sniffer.get_detections(limit)
    return {"status": "success", "total": len(detections), "detections": detections}

# Main entry point for testing
if __name__ == "__main__":
    # Test the sniffer
    sniffer = get_sniffer()
    print("Starting packet sniffer for 10 seconds...")
    sniffer.start_sniffing(timeout=10)
    import time
    time.sleep(5)
    print(f"Detections so far: {len(sniffer.detections)}")
    sniffer.stop_sniffing()
    print(f"Total detections: {len(sniffer.detections)}")