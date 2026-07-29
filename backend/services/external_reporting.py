import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class ExternalNetworkReporting:
    def __init__(self):
        self.templates = {
            "detailed": self._detailed_template,
            "summary": self._summary_template,
            "alert": self._alert_template
        }

    async def generate_report(self, findings: List[Dict], template: str = "detailed") -> Dict:
        template_func = self.templates.get(template, self._detailed_template)
        return await template_func(findings)

    async def _detailed_template(self, findings: List[Dict]) -> Dict:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "findings_count": len(findings),
            "findings": findings,
            "summary": self._generate_summary(findings)
        }

    async def _summary_template(self, findings: List[Dict]) -> Dict:
        severity = self._calculate_overall_severity(findings)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "summary": self._generate_summary(findings)
        }

    async def _alert_template(self, findings: List[Dict]) -> Dict:
        critical = [f for f in findings if f.get("severity") == "critical"]
        if not critical:
            return None
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "critical",
            "alert_type": "external_network_vulnerability",
            "details": critical
        }

    def _generate_summary(self, findings: List[Dict]) -> str:
        return f"Found {len(findings)} potential external vulnerabilities."

    def _calculate_overall_severity(self, findings: List[Dict]) -> str:
        sev = ["low", "medium", "high", "critical"]
        max_idx = 0
        for f in findings:
            s = f.get("severity", "low")
            if s in sev:
                idx = sev.index(s)
                if idx > max_idx:
                    max_idx = idx
        return sev[max_idx]