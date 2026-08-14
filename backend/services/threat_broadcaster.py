"""
SERA Threat Broadcaster
========================
Global asyncio queue that receives critical STYX detections and
broadcasts them to all connected WebSocket clients in real time.

Usage:
    from services.threat_broadcaster import push_threat, threat_manager

    # Push a threat from anywhere in the backend
    await push_threat({
        "severity": "CRITICAL",
        "type": "arp_spoof",
        "ip": "192.168.1.55",
        "detail": "ARP spoof detected — spoofed MAC aa:bb:cc:dd:ee:ff"
    })
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("sera.threat_broadcaster")

# Global queue — anyone in the backend can push threat events here
_threat_queue: asyncio.Queue = asyncio.Queue()


class ThreatConnectionManager:
    """Manages all active WebSocket connections for the threat stream."""

    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info(f"[THREATS] Client connected. Total: {len(self.active)}")

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info(f"[THREATS] Client disconnected. Total: {len(self.active)}")

    async def broadcast(self, message: dict):
        payload = json.dumps(message)
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


threat_manager = ThreatConnectionManager()


async def push_threat(event: dict):
    """
    Push a threat event into the queue.
    Called by STYX detector, security service, or any other detection module.
    """
    enriched = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    await _threat_queue.put(enriched)


async def threat_broadcast_loop():
    """
    Background coroutine — drains the queue and broadcasts to all
    connected WebSocket clients. Should be started in the FastAPI lifespan.
    """
    logger.info("[THREATS] Broadcast loop started.")
    while True:
        try:
            event = await _threat_queue.get()
            await threat_manager.broadcast({"type": "threat_alert", "data": event})
        except Exception as e:
            logger.error(f"[THREATS] Broadcast error: {e}")


THREAT_TEMPLATES = [
    {
        "severity": "CRITICAL",
        "title": "🚨 CRITICAL: Remote Code Execution (CVE-2026-1184)",
        "ip": "192.168.1.104",
        "detail": "STYX PRIME detected unauthenticated command injection payload on port 8080.",
        "action": "Isolate host immediately & apply vendor patch 4.2.1."
    },
    {
        "severity": "HIGH",
        "title": "⚠️ HIGH: ARP Poisoning & Man-In-The-Middle Detected",
        "ip": "10.0.4.12",
        "detail": "Duplicate MAC address 00:1A:2B:3C:4D:5E spoofing gateway router.",
        "action": "Enable Dynamic ARP Inspection (DAI) on Core Switch 01."
    },
    {
        "severity": "CRITICAL",
        "title": "🚨 CRITICAL: SSH Brute-Force & Privilege Escalation",
        "ip": "172.16.0.88",
        "detail": "Over 450 failed root SSH logins per minute from unauthorized subnet.",
        "action": "Enforce Fail2Ban IP block and disable root password auth."
    },
    {
        "severity": "HIGH",
        "title": "⚠️ HIGH: Exposed Database Admin Interface",
        "ip": "192.168.1.200",
        "detail": "Unencrypted PostgreSQL port 5432 exposed to external interface.",
        "action": "Restrict binding to 127.0.0.1 and enforce TLS certificates."
    }
]


async def auto_threat_generator_loop():
    """Generates continuous threat alerts for live STYX radar visualization."""
    import random
    logger.info("[THREATS] Auto threat generator loop started.")
    # Push initial threat immediately on connection
    await asyncio.sleep(3)
    await push_threat(random.choice(THREAT_TEMPLATES))
    
    while True:
        try:
            await asyncio.sleep(random.uniform(10.0, 18.0))
            threat = random.choice(THREAT_TEMPLATES)
            await push_threat(threat)
        except Exception as e:
            logger.error(f"[THREATS] Generator error: {e}")


def start_threat_services():
    """Helper to launch threat broadcast and generator loops on event loop."""
    asyncio.create_task(threat_broadcast_loop())
    asyncio.create_task(auto_threat_generator_loop())

