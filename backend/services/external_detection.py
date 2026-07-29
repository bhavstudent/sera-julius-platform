import logging
import random
from typing import List, Dict

logger = logging.getLogger(__name__)

class ExternalNetworkDetection:
    def __init__(self):
        self.detection_methods = ["ntp_timing"]  # Only NTP timing is relevant for external

    async def detect_external_networks(self, networks: List[Dict]) -> List[Dict]:
        """Detect vulnerabilities in external networks."""
        results = []
        for network in networks:
            findings = {}
            if "ntp_timing" in self.detection_methods:
                ntp_results = await self._detect_ntp_timing(network)
                findings.update(ntp_results)
            severity = self._calculate_severity(findings)
            if findings:
                results.append({
                    "network": network,
                    "findings": findings,
                    "severity": severity
                })
        return results

    async def _detect_ntp_timing(self, network: Dict) -> Dict:
        """Detect NTP timing anomalies."""
        host = network.get("hostname", "")
        if not host:
            return {}
        logger.info(f"[EXTERNAL] Analyzing NTP timing for {host}")
        # This is a placeholder – replace with actual NTP probing logic.
        # Example: send NTP query, measure response time and stratum.
        # For demo, we simulate a 20% chance of anomaly.
        anomaly = random.random() > 0.8
        variation = random.uniform(0, 500) if anomaly else 0
        return {
            "ntp_anomaly": anomaly,
            "timing_variation": variation,
            "response_time": random.uniform(10, 100)
        }

    def _calculate_severity(self, findings: Dict) -> str:
        if findings.get("ntp_anomaly", False):
            return "high"
        return "low"