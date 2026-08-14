#!/usr/bin/env python3
"""
network_scanner.py - Cross-platform host discovery
MERGED FROM JULIUS → SERA PLATFORM
Integration with Sera authentication, audit, and database
"""

import subprocess
import platform
import ipaddress
import concurrent.futures
import socket
import os
import re
import json
import logging
import sys
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
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
        logging.FileHandler(LOG_DIR / 'sera_network_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_network_scanner")

class SeraNetworkScanner:
    """Network scanner with Sera integration"""
    
    def __init__(self):
        self.is_scanning = False
        self.scan_results = []
        self.scan_history = []
        self.found_hosts = []
        self.current_scan = None
        
        # Sera components
        self.db = self._init_database()
        self.auth = self._init_auth()
        self.audit = self._init_audit()
        
        logger.info("Sera Network Scanner initialized")
    
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
    
    def get_local_ip(self) -> str:
        """Get local IP address (from Julius)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get network interfaces (from Julius)"""
        interfaces = []
        system = platform.system()
        
        try:
            if system == "Windows":
                output = subprocess.check_output("ipconfig", shell=True, text=True)
                lines = output.splitlines()
                current_iface = None
                
                for line in lines:
                    if "adapter" in line.lower():
                        current_iface = line.strip().replace("adapter", "").replace(":", "").strip()
                    elif "IPv4" in line and current_iface:
                        parts = line.split(":")
                        if len(parts) > 1:
                            ip = parts[1].strip()
                            if not ip.startswith("127."):
                                interfaces.append({
                                    "name": current_iface,
                                    "ip": ip,
                                    "os": "Windows"
                                })
            
            elif system == "Linux":
                output = subprocess.check_output(["ip", "addr"], text=True)
                for line in output.splitlines():
                    if "inet " in line and "127.0.0.1" not in line:
                        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                        if match:
                            interfaces.append({
                                "name": "Linux_interface",
                                "ip": match.group(1),
                                "os": "Linux"
                            })
            
            elif system == "Darwin":  # macOS
                output = subprocess.check_output(["ifconfig"], text=True)
                for line in output.splitlines():
                    if "inet " in line and "127.0.0.1" not in line:
                        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                        if match:
                            interfaces.append({
                                "name": "macOS_interface",
                                "ip": match.group(1),
                                "os": "macOS"
                            })
        
        except Exception as e:
            logger.warning(f"Could not detect network interfaces: {e}")
            ip = self.get_local_ip()
            interfaces.append({
                "name": "default",
                "ip": ip,
                "os": platform.system()
            })
        
        return interfaces
    
    def ping_host(self, ip: str, timeout: int = 2) -> bool:
        """Ping a host (from Julius)"""
        system = platform.system()
        try:
            if system == "Windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), str(ip)]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), str(ip)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+1)
            return result.returncode == 0
        except:
            return False
    
    def get_gateway(self) -> str:
        """Get default gateway (from Julius)"""
        system = platform.system()
        try:
            if system == "Windows":
                result = subprocess.run(["route", "print", "0.0.0.0"], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if "0.0.0.0" in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            for part in parts:
                                if re.match(r"^\d+\.\d+\.\d+\.\d+$", part):
                                    return part
            else:
                result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
                match = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", result.stdout)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.error(f"Error getting gateway: {e}")
        
        local_ip = self.get_local_ip()
        if local_ip != "127.0.0.1":
            parts = local_ip.split(".")
            parts[3] = "1"
            return ".".join(parts)
        
        return "192.168.1.1"
    
    def scan_network(self, ip_range: Optional[str] = None, 
                     max_workers: int = 50) -> List[str]:
        """Scan network for active hosts (from Julius with Sera integration)"""
        if self.is_scanning:
            logger.warning("Scan already in progress")
            return []
        
        self.is_scanning = True
        start_time = datetime.now()
        results = []
        
        try:
            # Determine IP range
            if not ip_range:
                local_ip = self.get_local_ip()
                if local_ip != "127.0.0.1":
                    base_ip = ".".join(local_ip.split(".")[:3])
                    ip_range = f"{base_ip}.0/24"
                else:
                    logger.error("Could not determine network range")
                    self.is_scanning = False
                    return []
            
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
            except ValueError:
                logger.error(f"Invalid IP range: {ip_range}")
                self.is_scanning = False
                return []
            
            logger.info(f"Scanning {ip_range} with {max_workers} threads...")
            
            def check_host(ip):
                if self.ping_host(str(ip)):
                    return str(ip)
                return None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = executor.map(check_host, network.hosts())
                results = [ip for ip in futures if ip]
            
            # Get network info
            interfaces = self.get_network_interfaces()
            gateway = self.get_gateway()
            
            # Create Sera scan result
            scan_result = {
                "timestamp": start_time.isoformat(),
                "ip_range": ip_range,
                "active_hosts": len(results),
                "hosts": results,
                "interfaces": interfaces,
                "gateway": gateway,
                "system": platform.system(),
                "scan_duration": (datetime.now() - start_time).total_seconds(),
                "source": "network_scanner"
            }
            
            # Store in Sera database
            self._store_scan_result(scan_result)
            
            # Log to Sera audit
            self._log_scan(scan_result)
            
            # Store in memory
            self.scan_history.append(scan_result)
            self.found_hosts.extend(results)
            self.current_scan = scan_result
            
            logger.info(f"Found {len(results)} active hosts")
            self.scan_results = results
            
        except Exception as e:
            logger.error(f"Scan error: {e}")
        finally:
            self.is_scanning = False
        
        return results
    
    def _store_scan_result(self, scan_result: Dict[str, Any]):
        """Store scan result in Sera database"""
        try:
            if self.db:
                cursor = self.db.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS network_scans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        ip_range TEXT,
                        active_hosts INTEGER,
                        hosts TEXT,
                        gateway TEXT,
                        system TEXT,
                        scan_duration REAL,
                        source TEXT
                    )
                ''')
                
                cursor.execute('''
                    INSERT INTO network_scans (
                        timestamp, ip_range, active_hosts, hosts, 
                        gateway, system, scan_duration, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scan_result['timestamp'],
                    scan_result['ip_range'],
                    scan_result['active_hosts'],
                    json.dumps(scan_result['hosts']),
                    scan_result['gateway'],
                    scan_result['system'],
                    scan_result['scan_duration'],
                    scan_result['source']
                ))
                self.db.commit()
        except Exception as e:
            logger.error(f"Error storing scan result: {e}")
    
    def _log_scan(self, scan_result: Dict[str, Any]):
        """Log scan to Sera audit"""
        try:
            if self.audit:
                self.audit(
                    action="network_scan",
                    target=scan_result['ip_range'],
                    details=scan_result
                )
            else:
                # Local fallback
                scan_file = LOG_DIR / f"scans_{datetime.now().strftime('%Y%m%d')}.log"
                with open(scan_file, 'a') as f:
                    f.write(json.dumps(scan_result) + '\n')
        except Exception as e:
            logger.error(f"Error logging scan: {e}")
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history"""
        return self.scan_history[-limit:]
    
    def get_scan_status(self) -> Dict[str, Any]:
        """Get current scan status"""
        return {
            "is_scanning": self.is_scanning,
            "total_hosts_found": len(set(self.found_hosts)),
            "total_scans": len(self.scan_history),
            "last_scan": self.current_scan
        }
    
    def clear_history(self):
        """Clear scan history"""
        self.found_hosts.clear()
        self.scan_history.clear()
        self.scan_results.clear()
        self.current_scan = None
        logger.info("Scan history cleared")
    
    def export_results(self, format: str = "json") -> str:
        """Export scan results"""
        if format == "json":
            return json.dumps({
                "scans": self.scan_history,
                "total_hosts": len(set(self.found_hosts))
            }, indent=2)
        elif format == "csv":
            output = "Timestamp,IP_Range,Active_Hosts,Gateway\n"
            for scan in self.scan_history:
                output += f"{scan['timestamp']},{scan['ip_range']},{scan['active_hosts']},{scan['gateway']}\n"
            return output
        return json.dumps(self.scan_history)

# Singleton for Sera
_scanner_instance = None

def get_scanner() -> SeraNetworkScanner:
    """Get or create scanner instance"""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = SeraNetworkScanner()
    return _scanner_instance

# Sera API Endpoints
def start_network_scan(ip_range: Optional[str] = None) -> Dict[str, Any]:
    """API endpoint: Start network scan"""
    scanner = get_scanner()
    
    # Run scan in background thread
    def scan_thread():
        scanner.scan_network(ip_range)
    
    thread = threading.Thread(target=scan_thread)
    thread.start()
    
    return {
        "status": "success",
        "message": "Network scan started",
        "ip_range": ip_range or "Auto-detected"
    }

def get_scan_status() -> Dict[str, Any]:
    """API endpoint: Get scan status"""
    scanner = get_scanner()
    return {"status": "success", "data": scanner.get_scan_status()}

def get_scan_results(limit: int = 10) -> Dict[str, Any]:
    """API endpoint: Get scan results"""
    scanner = get_scanner()
    scans = scanner.get_recent_scans(limit)
    return {"status": "success", "total": len(scans), "scans": scans}

# Main entry point for testing
if __name__ == "__main__":
    scanner = get_scanner()
    print("Starting network scan...")
    results = scanner.scan_network(max_workers=20)
    print(f"Found {len(results)} hosts")
    print(f"Gateway: {scanner.get_gateway()}")
    print(f"Interfaces: {scanner.get_network_interfaces()}")
