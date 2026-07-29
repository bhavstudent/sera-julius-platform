"""
SERA Censys Integration Service
=================================
Connects SERA to Censys internet-scan data for real-world
asset discovery and exposure analysis.

Requires:
    CENSYS_API_ID and CENSYS_API_SECRET in .env

Install:
    pip install censys
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from config import _config_instance as settings

logger = logging.getLogger("sera.censys")

# ─── Try importing censys library ────────────────────────────────────────────
try:
    from censys.search import CensysHosts
    from censys.common.exceptions import (
        CensysRateLimitExceededException,
        CensysUnauthorizedException,
        CensysNotFoundException,
    )
    CENSYS_AVAILABLE = True
except ImportError:
    CENSYS_AVAILABLE = False
    logger.warning("[CENSYS] censys library not installed. Run: pip install censys")


class CensysService:
    """
    SERA's Censys integration — provides real internet-scan data for:
      - Asset discovery (what ports/services are open on any IP)
      - Exposure analysis (what attackers can see about your infrastructure)
      - STYX detection enrichment (is this IP known/malicious?)
      - Recon agent data feed (real data instead of AI guessing)
    """

    def __init__(self):
        self.api_id = getattr(settings, "CENSYS_API_ID", "")
        self.api_secret = getattr(settings, "CENSYS_API_SECRET", "")
        self._client: Optional[Any] = None

        if CENSYS_AVAILABLE and self.api_id and self.api_secret:
            try:
                self._client = CensysHosts(api_id=self.api_id, api_secret=self.api_secret)
                logger.info("[CENSYS] Client initialized successfully.")
            except Exception as e:
                logger.warning(f"[CENSYS] Failed to initialize client: {e}")
        else:
            if not CENSYS_AVAILABLE:
                logger.warning("[CENSYS] Library not installed.")
            elif not self.api_id or not self.api_secret:
                logger.warning("[CENSYS] CENSYS_API_ID or CENSYS_API_SECRET not set in .env")

    @property
    def is_available(self) -> bool:
        return self._client is not None

    # ─── Core Methods ─────────────────────────────────────────────────────────

    async def lookup_ip(self, ip: str) -> Dict:
        """
        Full host data for a single IP from Censys.
        Returns: open ports, services, versions, TLS certs, geo, ASN.
        """
        if not self.is_available:
            return self._mock_host(ip)

        try:
            result = await asyncio.to_thread(self._client.view, ip)
            return self._format_host(result)
        except CensysNotFoundException:
            return {"ip": ip, "found": False, "message": "IP not indexed by Censys"}
        except CensysUnauthorizedException:
            logger.error("[CENSYS] Invalid credentials.")
            return self._mock_host(ip)
        except CensysRateLimitExceededException:
            logger.warning("[CENSYS] Rate limit hit.")
            return {"ip": ip, "error": "rate_limit", "message": "Censys rate limit exceeded. Retry later."}
        except Exception as e:
            logger.error(f"[CENSYS] lookup_ip({ip}) failed: {e}")
            return {"ip": ip, "error": str(e)}

    async def search_hosts(self, query: str, max_results: int = 25) -> List[Dict]:
        """
        Search Censys for hosts matching a query.
        Examples:
          - "services.port=22 and location.country=IN"
          - "services.software.product=Apache"
          - "autonomous_system.name=Cloudflare"
        """
        if not self.is_available:
            return self._mock_search(query)

        try:
            results = []
            pages = self._client.search(
                query,
                fields=["ip", "services.port", "services.service_name",
                        "services.software.product", "location.country",
                        "autonomous_system.name"],
                pages=1,
                per_page=min(max_results, 100)
            )
            for hit in pages:
                results.append({
                    "ip": hit.get("ip"),
                    "ports": [s.get("port") for s in hit.get("services", [])],
                    "services": [s.get("service_name") for s in hit.get("services", [])],
                    "country": hit.get("location", {}).get("country"),
                    "asn": hit.get("autonomous_system", {}).get("name"),
                })
                if len(results) >= max_results:
                    break
            return results
        except Exception as e:
            logger.error(f"[CENSYS] search_hosts failed: {e}")
            return []

    async def check_exposure(self, domain: str) -> Dict:
        """
        Check what is publicly visible for a domain — the attacker's view.
        Finds all IPs associated with the domain and their open ports/services.
        """
        if not self.is_available:
            return self._mock_exposure(domain)

        try:
            # Search for hosts referencing this domain in cert SANs or reverse DNS
            query = f'services.tls.certificates.leaf_data.names: "{domain}" or dns.reverse_dns.reverse_dns: "{domain}"'
            hosts = await self.search_hosts(query, max_results=20)

            exposed_ports = set()
            exposed_services = set()
            for h in hosts:
                exposed_ports.update(h.get("ports", []))
                exposed_services.update(s for s in h.get("services", []) if s)

            return {
                "domain": domain,
                "exposed_ips": len(hosts),
                "hosts": hosts,
                "unique_open_ports": sorted(list(exposed_ports)),
                "unique_services": list(exposed_services),
                "risk_score": self._calc_risk(list(exposed_ports)),
                "risk_level": self._risk_label(list(exposed_ports)),
            }
        except Exception as e:
            logger.error(f"[CENSYS] check_exposure({domain}) failed: {e}")
            return {"domain": domain, "error": str(e)}

    async def enrich_styx_detection(self, ip: str) -> Dict:
        """
        Enrich a STYX detection with Censys context:
          - Is this IP known? What services does it run?
          - Is it an exit node / Tor / VPN / known attacker infra?
          - What country/ASN is it from?
        Used to determine if a detected NTP/ARP anomaly is from known malicious infra.
        """
        host_data = await self.lookup_ip(ip)
        enriched = {
            "ip": ip,
            "censys_data": host_data,
            "threat_context": self._assess_threat(host_data),
        }
        return enriched

    async def get_recon_data(self, target_scope: str) -> Dict:
        """
        Called by SecurityOrchestrator ReconAgent to get REAL data
        instead of AI-guessing. Parses IPs/domains from target scope
        and returns actual Censys findings.
        """
        import re
        # Extract IPs and domains from scope string
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b'
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'

        ips = re.findall(ip_pattern, target_scope)
        domains = re.findall(domain_pattern, target_scope)

        results = {"scope": target_scope, "hosts": [], "exposures": []}

        # Lookup each IP
        for ip in ips[:5]:  # limit to 5
            host = await self.lookup_ip(ip.split("/")[0])
            results["hosts"].append(host)

        # Check each domain's exposure
        for domain in domains[:3]:  # limit to 3
            exposure = await self.check_exposure(domain)
            results["exposures"].append(exposure)

        return results

    # ─── Formatting helpers ────────────────────────────────────────────────────

    def _format_host(self, raw: dict) -> dict:
        services = raw.get("services", [])
        return {
            "ip": raw.get("ip"),
            "found": True,
            "last_updated": raw.get("last_updated_at"),
            "country": raw.get("location", {}).get("country"),
            "city": raw.get("location", {}).get("city"),
            "asn": raw.get("autonomous_system", {}).get("asn"),
            "asn_name": raw.get("autonomous_system", {}).get("name"),
            "open_ports": [s.get("port") for s in services],
            "services": [
                {
                    "port": s.get("port"),
                    "name": s.get("service_name"),
                    "product": s.get("software", [{}])[0].get("product") if s.get("software") else None,
                    "version": s.get("software", [{}])[0].get("version") if s.get("software") else None,
                    "banner": s.get("banner", "")[:200] if s.get("banner") else None,
                }
                for s in services
            ],
            "tls_certs": [
                {
                    "names": cert.get("leaf_data", {}).get("names", []),
                    "issuer": cert.get("leaf_data", {}).get("issuer", {}).get("organization"),
                    "expires": cert.get("leaf_data", {}).get("not_after"),
                }
                for s in services
                for cert in (s.get("tls", {}).get("certificates", []) or [])
            ][:3],
        }

    def _calc_risk(self, ports: list) -> int:
        """Score 0-100 based on dangerous open ports."""
        risky = {21, 22, 23, 25, 445, 3389, 5900, 6379, 27017, 5432, 3306}
        score = min(100, len(set(ports) & risky) * 20)
        return score

    def _risk_label(self, ports: list) -> str:
        score = self._calc_risk(ports)
        if score >= 60: return "Critical"
        if score >= 40: return "High"
        if score >= 20: return "Medium"
        return "Low"

    def _assess_threat(self, host: dict) -> dict:
        ports = host.get("open_ports", [])
        return {
            "is_known_attacker_infra": 6379 in ports or 27017 in ports,  # Redis/Mongo exposed
            "has_rdp_exposed": 3389 in ports,
            "has_ssh_exposed": 22 in ports,
            "has_smb_exposed": 445 in ports,
            "risk_level": self._risk_label(ports),
            "risk_score": self._calc_risk(ports),
        }

    # ─── Mock responses when Censys not configured ────────────────────────────

    def _mock_host(self, ip: str) -> dict:
        return {
            "ip": ip, "found": True, "mock": True,
            "country": "US", "asn_name": "Example ISP",
            "open_ports": [22, 80, 443],
            "services": [
                {"port": 22, "name": "SSH", "product": "OpenSSH", "version": "8.9"},
                {"port": 443, "name": "HTTPS", "product": "nginx", "version": "1.24.0"},
            ],
            "note": "Mock data — set CENSYS_API_ID and CENSYS_API_SECRET in .env for real data"
        }

    def _mock_search(self, query: str) -> list:
        return [{"ip": "1.2.3.4", "ports": [80, 443], "services": ["HTTP", "HTTPS"],
                 "country": "US", "asn": "Example", "mock": True}]

    def _mock_exposure(self, domain: str) -> dict:
        return {
            "domain": domain, "exposed_ips": 1, "mock": True,
            "unique_open_ports": [80, 443], "unique_services": ["HTTP", "HTTPS"],
            "risk_score": 0, "risk_level": "Low",
            "note": "Mock data — set CENSYS_API_ID and CENSYS_API_SECRET in .env for real data"
        }


# Global singleton
censys_service = CensysService()
