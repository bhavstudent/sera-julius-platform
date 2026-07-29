import logging
from typing import List, Dict
from datetime import datetime
from sqlalchemy import select
from database import async_session_maker
from models.security import STYXDetection, STYXNode, STYXReport
from services.ntp_monitor import NTPMonitor
from services.arp_monitor import ARPMonitor
from services.threat_broadcaster import push_threat

logger = logging.getLogger(__name__)


class STYXPrimeDetector:
    """Detects STYX PRIME (zero‑input) attack signatures."""

    async def detect_ntp_anomalies(self, network_scope: str) -> List[Dict]:
        """Run NTP monitor and store results."""
        logger.info(f"[STYX] NTP anomaly detection for {network_scope}")
        monitor = NTPMonitor()
        anomalies = monitor.start_monitoring(network_scope, timeout=10)

        # Store in database
        async with async_session_maker() as session:
            for a in anomalies:
                detection = STYXDetection(
                    network_scope=network_scope,
                    device_ip=a["ip"],
                    detection_pattern="ntp_timing_anomaly",
                    severity=a["severity"],
                    details=f"Stratum anomaly: {a.get('variation', '')}"
                )
                session.add(detection)
            await session.commit()

        # Push CRITICAL/HIGH threats to real-time WebSocket broadcaster
        for a in anomalies:
            if a.get("severity") in ("HIGH", "CRITICAL"):
                await push_threat({
                    "severity": a["severity"],
                    "type": "ntp_anomaly",
                    "title": "🚨 NTP Timing Anomaly Detected",
                    "detail": f"Suspicious NTP packet from {a['ip']}: {a.get('variation', 'Stratum anomaly')}",
                    "ip": a["ip"],
                    "network_scope": network_scope,
                    "action": "Possible time-sync manipulation attack. Check for nation-state activity."
                })

        return anomalies

    async def detect_bmc_attacks(self, network_scope: str) -> List[Dict]:
        """Run ARP monitor and store results."""
        logger.info(f"[STYX] BMC attack detection for {network_scope}")
        monitor = ARPMonitor()
        attacks = monitor.start_monitoring(network_scope, timeout=10)

        async with async_session_maker() as session:
            for a in attacks:
                detection = STYXDetection(
                    network_scope=network_scope,
                    device_ip=a["ip"],
                    detection_pattern="bmc_arp_spoof",
                    severity=a["severity"],
                    details=f"Spoofed MAC: {a.get('spoofed_mac', '')}"
                )
                session.add(detection)
            await session.commit()

        # Push ARP spoof threats to real-time broadcaster immediately
        for a in attacks:
            await push_threat({
                "severity": "CRITICAL",
                "type": "arp_spoof",
                "title": "🚨 ARP SPOOFING DETECTED — Network Hijacking Attempt",
                "detail": f"IP {a['ip']} is being spoofed with MAC {a.get('spoofed_mac', '??')}. Someone may be intercepting your traffic.",
                "ip": a["ip"],
                "spoofed_mac": a.get("spoofed_mac", ""),
                "network_scope": network_scope,
                "action": "IMMEDIATE ACTION REQUIRED: ARP cache poisoning detected. Isolate affected segment."
            })

        return attacks

    async def detect_propagation(self, network_scope: str) -> List[Dict]:
        """Analyze existing STYX nodes to map propagation paths."""
        logger.info(f"[STYX] Propagation detection for {network_scope}")
        async with async_session_maker() as session:
            # Get all infected nodes
            stmt = select(STYXNode).where(STYXNode.infection_status == "INFECTED")
            nodes = (await session.execute(stmt)).scalars().all()

            # Build parent-child graph
            graph = {}
            for node in nodes:
                if node.parent_node:
                    if node.parent_node not in graph:
                        graph[node.parent_node] = []
                    graph[node.parent_node].append(node.ip_address)

            paths = [
                {"parent": parent, "children": children, "infection_level": len(children)}
                for parent, children in graph.items()
            ]
            return paths

    async def generate_threat_report(self, network_scope: str) -> Dict:
        """Compile all detections and build a structured report."""
        async with async_session_maker() as session:
            # Fetch detections
            det_result = await session.execute(
                select(STYXDetection).where(
                    STYXDetection.network_scope == network_scope,
                    STYXDetection.is_active == True
                )
            )
            detections = det_result.scalars().all()

            # Fetch infected nodes
            node_result = await session.execute(
                select(STYXNode).where(STYXNode.infection_status == "INFECTED")
            )
            nodes = node_result.scalars().all()

            # Fetch parents (for propagation)
            parent_result = await session.execute(
                select(STYXNode).where(STYXNode.node_type == "infected_parent")
            )
            parents = parent_result.scalars().all()

            report = {
                "network_scope": network_scope,
                "detected_detections": len(detections),
                "infected_nodes": len(nodes),
                "detection_timeline": [
                    {
                        "timestamp": d.detection_time.isoformat(),
                        "device": d.device_ip,
                        "pattern": d.detection_pattern,
                        "severity": d.severity,
                        "details": d.details,
                    }
                    for d in detections
                ],
                "infection_map": [
                    {
                        "node_id": n.node_id,
                        "ip": n.ip_address,
                        "type": n.node_type,
                        "parent": n.parent_node,
                        "last_seen": n.last_seen.isoformat(),
                    }
                    for n in nodes
                ],
                "propagation_paths": [
                    {
                        "parent": p.node_id,
                        "children": [
                            child.ip_address for child in nodes
                            if child.parent_node == p.node_id
                        ],
                        "infection_level": len([n for n in nodes if n.parent_node == p.node_id])
                    }
                    for p in parents
                ]
            }

            # Store the report
            report_obj = STYXReport(
                network_scope=network_scope,
                report_data=report
            )
            session.add(report_obj)
            await session.commit()

            return report