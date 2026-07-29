# backend/services/autonomous_scanner.py
import asyncio
import random
import logging
from typing import List, Dict

from services.target_discovery import GlobalTargetDiscovery
from services.security_service import STYXPrimeDetector

logger = logging.getLogger(__name__)

class AutonomousScanner:
    def __init__(self):
        self.discovery = GlobalTargetDiscovery()
        self.detector = STYXPrimeDetector()
        self.running = False
        
    async def start(self):
        """Start scanning all public NTP servers"""
        self.running = True
        logger.info("[STYX] Autonomous scanner started.")
        while self.running:
            try:
                # Discover new targets
                targets = await self.discovery.discover_targets(limit=100)
                logger.info(f"[STYX] Discovered {len(targets)} targets.")
                
                # Process targets concurrently
                tasks = []
                for target in targets:
                    task = asyncio.create_task(self._scan_target(target))
                    tasks.append(task)
                
                # Wait for completion
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Sleep before next batch
                sleep_time = random.uniform(30, 120)
                logger.info(f"[STYX] Sleeping for {sleep_time:.0f}s before next batch.")
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"[STYX] Scanner error: {e}")
                await asyncio.sleep(60)
    
    async def _scan_target(self, target: Dict):
        """Scan a single target"""
        try:
            hostname = target["hostname"]
            logger.debug(f"[STYX] Scanning {hostname}")
            # Run STYX detection – we need to adapt to existing detector methods.
            # The detector currently scans a network scope; we can treat hostname as a /32.
            results = await self.detector.detect_ntp_anomalies(hostname)
            # Store results – you may want to call generate_threat_report or store directly.
            if results:
                # We can store the results in the database via the detector's internal methods
                # or call generate_threat_report which already stores a report.
                # For simplicity, we'll just generate a report for this host.
                await self.detector.generate_threat_report(hostname)
                logger.info(f"[STYX] Scan complete for {hostname}: {len(results)} anomalies.")
        except Exception as e:
            logger.error(f"[STYX] Error scanning {target['hostname']}: {e}")
    
    def stop(self):
        self.running = False
        logger.info("[STYX] Autonomous scanner stopped.")