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
    "blocked_duplicate_discoveries": 0,
    "scan_targets_this_cycle": 0,
    "compounding_growth_rate": 1.0,  # Compounding multiplier factor
    "entities_learned_per_min": 2,
    "graph_edges_learned_per_min": 8,
    "threats_learned_per_min": 4,
    "styx_attacks_executed": 14,
    "julius_untraceability_index": 99.4,
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
    {"title": "⚠️ HIGH: ARP Poisoning & MitM Executed & Resolved", "ip": "10.0.4.12", "severity": "HIGH",
     "detail": "STYX spoofed gateway router on VLAN 10. Julius extracted network routing topologies."},
    {"title": "🚨 CRITICAL: SSH Brute-Force & Zero-Touch Shell", "ip": "172.16.0.88", "severity": "CRITICAL",
     "detail": "STYX autonomous payload executed shell exploitation and erased local syslog traces."},
    {"title": "⚠️ HIGH: BGP Route Hijack & Subnet Spoof", "ip": "198.20.69.74", "severity": "HIGH",
     "detail": "STYX route injector launched BGP autonomous network redirection test on Kali bridge."},
    {"title": "🚨 CRITICAL: Zero-Day CVE-2026-1184 Exploitation", "ip": "185.220.101.5", "severity": "CRITICAL",
     "detail": "STYX autonomous scanner executed CVE-2026-1184 exploit chain; fed causal trace to Julius AI."},
]


async def _event_simulator_loop():
    """Tracks live events-per-second using a rolling 60-second in-memory window."""
    logger.info("[LIVE ENGINE] Event simulator loop started (in-memory rolling window).")
    window_events: list[float] = []

    while True:
        try:
            # Simulate a burst of arriving events incorporating compounding factor
            compound_mult = _live_state.get("compounding_growth_rate", 1.0)
            batch_size = int(random.randint(6, 22) * compound_mult)
            now = asyncio.get_event_loop().time()

            for _ in range(batch_size):
                window_events.append(now)

            cutoff = now - 60.0
            window_events = [t for t in window_events if t > cutoff]

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
    """Tracks live active alert count, triggers STYX attack cycles, and updates Julius untraceability."""
    logger.info("[LIVE ENGINE] Alert counter & STYX feedback loop started.")
    from services.threat_broadcaster import push_threat

    await asyncio.sleep(1)
    await push_threat(random.choice(THREAT_TYPES))
    _live_state["active_alerts"] = random.randint(3, 8)

    while True:
        try:
            interval = random.uniform(3, 6)
            await asyncio.sleep(interval)


            threat = random.choice(THREAT_TYPES)
            await push_threat(threat)

            # STYX Attack Execution & Julius Untraceability Progression
            _live_state["styx_attacks_executed"] += 1
            _live_state["julius_untraceability_index"] = min(99.99, round(_live_state["julius_untraceability_index"] + 0.03, 2))

            if random.random() < 0.6:
                _live_state["active_alerts"] = min(_live_state["active_alerts"] + random.randint(1, 3), 24)
            else:
                _live_state["active_alerts"] = max(_live_state["active_alerts"] - random.randint(0, 2), 0)

        except Exception as e:
            logger.warning(f"[LIVE ENGINE] Alert counter error: {e}")
            await asyncio.sleep(5)


async def _entity_discovery_loop():
    """
    Simulates autonomous AI discovering new entities with:
    1. Real-Time Blocking Identity Resolution (Deduplication)
    2. Geometric Compounding Acceleration Loop
    """
    logger.info("[LIVE ENGINE] Compounding entity discovery loop with inline Identity Resolution started.")
    from core.entity_resolution import entity_registry
    from services.identity_resolution import identity_resolver
    import uuid

    SECTORS = ["Financial Services", "Healthcare", "Technology", "Energy", "Industrial"]
    COUNTRIES = ["US", "UK", "DE", "JP", "SG", "CH", "FR", "AU", "CA", "IN"]

    await asyncio.sleep(1)
    cycle = 0

    while True:
        try:
            cycle += 1
            # ── 1. GEOMETRIC COMPOUNDING LOOP ACCELERATION ──
            # Rate accelerates over time as SERA discovers more connections & graph nodes
            _live_state["compounding_growth_rate"] = round(1.0 + (cycle * 0.08), 2)
            _live_state["entities_learned_per_min"] = int(2 * _live_state["compounding_growth_rate"])
            _live_state["graph_edges_learned_per_min"] = int(8 * _live_state["compounding_growth_rate"])
            _live_state["threats_learned_per_min"] = int(4 * _live_state["compounding_growth_rate"])

            interval = random.uniform(3, 6)
            await asyncio.sleep(interval)


            # Discover compounding batch
            new_count = random.randint(1, 3)
            for _ in range(new_count):
                name_parts = [
                    random.choice(["Global", "International", "Pacific", "Atlantic", "Euro", "Nordic", "Asia", "Apex", "Styx", "JPMorgan", "Apple", "Microsoft"]),
                    random.choice(["Capital", "Tech", "Health", "Energy", "Systems", "Solutions", "Dynamics", "Cyber", "Quantum", "Chase", "Inc", "Corp"]),
                    random.choice(["Corp", "Ltd", "AG", "plc", "Inc", "GmbH", "SA", ""]),
                ]
                candidate_name = " ".join([p for p in name_parts if p]).strip()

                # ── 2. INLINE BLOCKING DEDUPLICATION / IDENTITY RESOLUTION ──
                is_duplicate, canonical_id, sim_score = identity_resolver.resolve_entity(
                    candidate_name, entity_registry.entities
                )

                if is_duplicate:
                    # BLOCKED INLINE! Do not create duplicate entity record.
                    _live_state["blocked_duplicate_discoveries"] += 1
                    logger.info(
                        f"[SERA BLOCKING IDENTITY RESOLUTION] Prevented duplicate '{candidate_name}' "
                        f"(Similarity {sim_score:.2f} to canonical {canonical_id})."
                    )
                    continue

                # PASSES: Distinct entity created
                eid = str(uuid.uuid4())
                entity_registry.entities[eid] = {
                    "id": eid,
                    "name": candidate_name,
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
                _live_state["total_entities"] = len(entity_registry.entities)

        except Exception as e:
            logger.warning(f"[LIVE ENGINE] Entity discovery error: {e}")
            await asyncio.sleep(10)


async def _eps_resetter_loop():
    """Resets events_last_minute every 60 seconds for accurate EPS calculation."""
    while True:
        await asyncio.sleep(60)
        _live_state["events_last_minute"] = 0


def start_live_engine():
    """Launch live engine background tasks. When real data mode is active and synthetic noise is disabled, only tracking loops run."""
    import os
    enable_noise = os.getenv("ENABLE_SYNTHETIC_NOISE", "false").lower() in ("true", "1", "yes")
    use_real = os.getenv("USE_REAL_DATA", "true").lower() in ("true", "1", "yes")

    asyncio.create_task(_eps_resetter_loop())

    if enable_noise or not use_real:
        asyncio.create_task(_event_simulator_loop())
        asyncio.create_task(_alert_counter_loop())
        asyncio.create_task(_entity_discovery_loop())
        logger.info("[LIVE ENGINE] Synthetic activity loops enabled.")
    else:
        logger.info("[LIVE ENGINE] Real-data mode active — synthetic fake noise loops SILENCED.")



