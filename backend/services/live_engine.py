"""
SERA Real-Time Live Activity Engine
====================================
Generates continuous synthetic telemetry events, active alert tracking,
and live entity discovery to make the dashboard feel alive and real-time.

This engine runs as background asyncio tasks on startup and continuously:
- Inserts synthetic protocol events (SWIFT, FHIR, MQTT, HTTP) into the DB
- Maintains an in-memory live alert counter
- Tracks entity discovery growth
- Feeds the threat broadcaster with periodic alerts
"""

import asyncio
import random
import logging
import time
from datetime import datetime, timezone

logger = logging.getLogger("sera.live_engine")

# ─── In-Memory Live State ──────────────────────────────────────────────────────
_live_state = {
    "events_per_second": 0.0,
    "events_last_minute": 0,
    "active_alerts": 0,
    "total_events": 0,
    "entity_discoveries": 0,
    "scan_targets_this_cycle": 0,
    "last_update": 0.0,
}

def get_live_state():
    return dict(_live_state)


# ─── Protocols & Payloads ─────────────────────────────────────────────────────
PROTOCOLS = ["SWIFT", "FHIR", "MQTT", "HTTP", "HTTPS", "gRPC", "WebSocket", "AMQP"]
ENTITY_NAMES = [
    "JPMorgan Chase", "BlackRock", "Goldman Sachs", "HSBC", "Deutsche Bank",
    "Pfizer Inc", "Moderna Inc", "Johnson & Johnson", "AstraZeneca", "Novartis",
    "Apple Inc", "Microsoft Corp", "Alphabet Inc", "Amazon AWS", "Meta Platforms",
    "Tesla Inc", "Nvidia Corp", "TSMC", "Samsung Electronics", "Intel Corp",
    "Shell plc", "ExxonMobil", "BP plc", "TotalEnergies", "Chevron Corp",
    "Siemens AG", "ABB Ltd", "Honeywell", "General Electric", "Bosch Group",
]

THREAT_TYPES = [
    {"title": "🚨 CRITICAL: SQL Injection Attempt Detected", "ip": "45.33.32.156", "severity": "CRITICAL",
     "detail": "STYX PRIME detected malicious SQL payload on API gateway port 443."},
    {"title": "⚠️ HIGH: ARP Poisoning & MitM Detected", "ip": "10.0.4.12", "severity": "HIGH",
     "detail": "Duplicate MAC 00:1A:2B:3C:4D:5E spoofing gateway router on VLAN 10."},
    {"title": "🚨 CRITICAL: SSH Brute-Force & Privilege Escalation", "ip": "172.16.0.88", "severity": "CRITICAL",
     "detail": "Over 450 failed root SSH logins per minute from unauthorized subnet."},
    {"title": "⚠️ HIGH: Exposed Redis Port 6379", "ip": "198.20.69.74", "severity": "HIGH",
     "detail": "Unauthenticated Redis 6379 exposed to external internet — data exfiltration risk."},
    {"title": "🚨 CRITICAL: Zero-Day CVE-2026-1184 Exploitation", "ip": "185.220.101.5", "severity": "CRITICAL",
     "detail": "STYX autonomous scanner detected active exploitation of CVE-2026-1184 on port 8080."},
    {"title": "⚠️ HIGH: PostgreSQL Exposed to Internet", "ip": "192.168.1.200", "severity": "HIGH",
     "detail": "Unencrypted PostgreSQL port 5432 bound to 0.0.0.0 — immediate patching required."},
    {"title": "⚠️ MEDIUM: GDELT Geopolitical Anomaly Spike", "ip": "80.82.77.33", "severity": "MEDIUM",
     "detail": "GDELT conflict event density spiked 340% in Central Asia — elevated risk score."},
    {"title": "🚨 CRITICAL: Ransomware Lateral Movement Detected", "ip": "66.240.192.138", "severity": "CRITICAL",
     "detail": "Suspicious SMB traffic pattern consistent with LockBit 3.0 lateral spread detected."},
]


async def _event_simulator_loop():
    """Tracks live events-per-second using a rolling 60-second in-memory window.
    No DB writes required — avoids FK constraint violations entirely.
    """
    logger.info("[LIVE ENGINE] Event simulator loop started (in-memory rolling window).")
    window_events: list[float] = []  # timestamps of simulated events in last 60s

    while True:
        try:
            # Simulate a burst of arriving events
            batch_size = random.randint(6, 22)
            now = asyncio.get_event_loop().time()

            for _ in range(batch_size):
                window_events.append(now)

            # Evict events older than 60 seconds
            cutoff = now - 60.0
            window_events = [t for t in window_events if t > cutoff]

            # Compute accurate EPS from rolling window
            eps = round(len(window_events) / 60.0, 2)
            _live_state["events_per_second"] = eps
            _live_state["total_events"] += batch_size
            _live_state["events_last_minute"] = len(window_events)
            _live_state["last_update"] = time.time()

            await asyncio.sleep(random.uniform(0.8, 2.2))

        except Exception as e:
            logger.warning(f"[LIVE ENGINE] Event simulator error: {e}")
            await asyncio.sleep(3)



async def _alert_counter_loop():
    """Tracks live active alert count and feeds threat broadcaster."""
    logger.info("[LIVE ENGINE] Alert counter loop started.")
    from services.threat_broadcaster import push_threat

    # Push first alert immediately
    await asyncio.sleep(2)
    await push_threat(random.choice(THREAT_TYPES))
    _live_state["active_alerts"] = random.randint(3, 8)

    while True:
        try:
            interval = random.uniform(12, 28)
            await asyncio.sleep(interval)

            threat = random.choice(THREAT_TYPES)
            await push_threat(threat)

            # Alerts grow and auto-resolve over time
            if random.random() < 0.6:
                _live_state["active_alerts"] = min(
                    _live_state["active_alerts"] + random.randint(1, 3), 24
                )
            else:
                _live_state["active_alerts"] = max(
                    _live_state["active_alerts"] - random.randint(0, 2), 0
                )

            logger.debug(f"[LIVE ENGINE] Active alerts: {_live_state['active_alerts']}")

        except Exception as e:
            logger.warning(f"[LIVE ENGINE] Alert counter error: {e}")
            await asyncio.sleep(5)


async def _entity_discovery_loop():
    """Simulates autonomous AI discovering new entities from live data sources."""
    logger.info("[LIVE ENGINE] Entity discovery loop started.")
    from core.entity_resolution import entity_registry
    import uuid

    SECTORS = ["Financial Services", "Healthcare", "Technology", "Energy", "Industrial"]
    COUNTRIES = ["US", "UK", "DE", "JP", "SG", "CH", "FR", "AU", "CA", "IN"]

    await asyncio.sleep(3)
    while True:
        try:
            interval = random.uniform(10, 20)
            await asyncio.sleep(interval)

            # Discover 1-3 new entities per cycle
            new_count = random.randint(1, 3)
            for _ in range(new_count):
                eid = str(uuid.uuid4())
                name_parts = [
                    random.choice(["Global", "International", "Pacific", "Atlantic", "Euro", "Nordic", "Asia", "Apex", "Styx"]),
                    random.choice(["Capital", "Tech", "Health", "Energy", "Systems", "Solutions", "Dynamics", "Cyber", "Quantum"]),
                    random.choice(["Corp", "Ltd", "AG", "plc", "Inc", "GmbH", "SA"]),
                ]
                name = " ".join(name_parts)
                entity_registry.entities[eid] = {
                    "id": eid,
                    "name": name,
                    "domain": random.choice(["financial", "healthcare", "iot", "social"]),
                    "status": random.choice(["stable", "stable", "pre-transition"]),
                    "entropy": random.uniform(0.1, 1.9),
                    "event_count": random.randint(0, 150),
                    "alert_count": random.randint(0, 3),
                    "ticker": None,
                    "sector": random.choice(SECTORS),
                    "country": random.choice(COUNTRIES),
                    "source": "AI_DISCOVERY",
                }
                _live_state["entity_discoveries"] += 1
                _live_state["total_entities"] = 59 + _live_state["entity_discoveries"]

        except Exception as e:
            logger.warning(f"[LIVE ENGINE] Entity discovery error: {e}")
            await asyncio.sleep(10)


async def _eps_resetter_loop():
    """Resets events_last_minute every 60 seconds for accurate EPS calculation."""
    while True:
        await asyncio.sleep(60)
        _live_state["events_last_minute"] = 0


def start_live_engine():
    """Launch all live engine background tasks. Call from FastAPI startup."""
    asyncio.create_task(_event_simulator_loop())
    asyncio.create_task(_alert_counter_loop())
    asyncio.create_task(_entity_discovery_loop())
    asyncio.create_task(_eps_resetter_loop())
    logger.info("[LIVE ENGINE] All real-time live activity engine tasks started.")
