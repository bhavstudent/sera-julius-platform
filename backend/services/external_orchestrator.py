import logging
from datetime import datetime
from typing import Dict

from services.external_discovery import ExternalNetworkDiscovery
from services.external_detection import ExternalNetworkDetection
from services.external_reporting import ExternalNetworkReporting

logger = logging.getLogger(__name__)

class ExternalNetworkOrchestrator:
    def __init__(self):
        self.discovery = ExternalNetworkDiscovery()
        self.detection = ExternalNetworkDetection()
        self.reporting = ExternalNetworkReporting()
        self.state = {
            "last_discovery": None,
            "last_detection": None,
            "reports": []
        }

    async def run_cycle(self) -> Dict:
        """Run a complete cycle for external networks."""
        try:
            logger.info("[EXTERNAL] Orchestrator: starting cycle.")
            self.state["current_phase"] = "discovery"
            networks = await self.discovery.discover_external_networks()
            logger.info(f"[EXTERNAL] Discovered {len(networks)} external networks.")

            self.state["current_phase"] = "detection"
            findings = await self.detection.detect_external_networks(networks)
            logger.info(f"[EXTERNAL] Detection complete. {len(findings)} findings.")

            self.state["current_phase"] = "reporting"
            report = None
            if findings:
                report = await self.reporting.generate_report(findings, "detailed")
                self.state["reports"].append(report)
            else:
                report = {"message": "No findings"}

            self.state["last_run"] = datetime.utcnow()
            logger.info("[EXTERNAL] Orchestrator cycle complete.")
            return report or {"message": "No findings"}
        except Exception as e:
            logger.error(f"[EXTERNAL] Orchestrator cycle failed: {e}")
            return {"error": str(e)}