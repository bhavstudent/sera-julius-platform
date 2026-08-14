import logging
import re
from datetime import datetime
from sqlalchemy import select, desc
from database import async_session_maker
from models.commerce import NewsEventsModel

logger = logging.getLogger("sera.dark_intel_service")

THREAT_KEYWORDS = [
    "breach", "hack", "ransomware", "leak", "vulnerability",
    "exploit", "cyberattack", "compromise", "backdoor",
    "infiltration", "malware", "adversary", "threat", "espionage",
    "cyber", "attack", "stolen", "intercepted", "anomalous"
]

class DarkIntelService:
    @classmethod
    async def get_briefings(cls, clearance: str = "ALL") -> list:
        """
        Query NewsEventsModel for threat keywords.
        Calculate severity based on keyword density.
        If DB is empty, fall back to live GDELT cybersecurity news.
        Filter by clearance parameter if not 'ALL'.
        """
        try:
            async with async_session_maker() as session:
                stmt = select(NewsEventsModel).order_by(desc(NewsEventsModel.date)).limit(100)
                res = await session.execute(stmt)
                news_items = res.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching news events: {e}", exc_info=True)
            news_items = []

        briefings = []
        for n in news_items:
            title_lower = n.title.lower()
            matches = [kw for kw in THREAT_KEYWORDS if kw in title_lower]
            density = len(set(matches))
            if density == 0:
                if any(w in title_lower for w in ["security", "intel", "signal", "node", "critical"]):
                    density = 1
                else:
                    continue

            if density >= 3:
                severity = "critical"; classification = "EYES ONLY"
                clearance_level = "LEVEL 5 (ADMIN)"; expires_in = 180
            elif density == 2:
                severity = "high"; classification = "TOP SECRET"
                clearance_level = "LEVEL 4 (DIRECTOR)"; expires_in = 300
            elif density == 1:
                severity = "medium"; classification = "SECRET"
                clearance_level = "LEVEL 3 (ANALYST)"; expires_in = 600
            else:
                severity = "low"; classification = "RESTRICTED"
                clearance_level = "LEVEL 2 (OPERATOR)"; expires_in = 900

            words = n.title.split() + (n.themes or "").split()
            summary_words = (n.title + ". " + (n.themes or "")).split()
            redacted_words = []
            for idx, word in enumerate(summary_words):
                clean_word = re.sub(r'[^\w]', '', word)
                if (idx % 4 == 0) or (clean_word.isupper() and len(clean_word) > 1) or clean_word.isdigit():
                    redacted_words.append("[REDACTED]")
                else:
                    redacted_words.append(word)
            redacted_content = " ".join(redacted_words)
            if not redacted_content.strip():
                redacted_content = "SIGNAL STRENGTH: [REDACTED] // PACKET METRIC: [REDACTED]"

            briefings.append({
                "id": n.id,
                "title": n.title,
                "summary": f"Threat analysis: {n.title}. Causal vectors detected anomalous behavior. Severity: {severity.upper()}.",
                "classification": classification,
                "severity": severity,
                "clearance_level": clearance_level,
                "source": "SIGINT-KRONOS" if n.tone < 0 else "AXIOM-Tracker",
                "date": n.date.strftime("%Y-%m-%d %H:%M:%S") if n.date else "Recent",
                "expires_in": expires_in,
                "redacted_content": redacted_content,
                "tags": matches if matches else ["threat"]
            })

        # ── REAL FALLBACK: Live GDELT cybersecurity news ──────────────────────
        if not briefings:
            try:
                import httpx
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    r = await client.get(
                        "https://api.gdeltproject.org/api/v2/doc/doc",
                        params={
                            "query": "cybersecurity breach hack ransomware vulnerability exploit",
                            "mode": "artlist", "maxrecords": "6", "format": "json",
                            "timespan": "7d", "sort": "DateDesc"
                        },
                        timeout=httpx.Timeout(3.0),
                        headers={"User-Agent": "SERA-Platform/2.0"}
                    )
                    if r.status_code == 200:
                        articles = r.json().get("articles", [])[:6]
                        for i, a in enumerate(articles):
                            title = a.get("title", "Threat Intelligence Report")
                            domain = a.get("domain", "Unknown Source")
                            url = a.get("url", "")
                            severity = "critical" if i < 2 else ("high" if i < 4 else "medium")
                            cls_label = "EYES ONLY" if i < 2 else ("TOP SECRET" if i < 4 else "SECRET")
                            lvl = "LEVEL 5 (ADMIN)" if i < 2 else ("LEVEL 4 (DIRECTOR)" if i < 4 else "LEVEL 3 (ANALYST)")
                            briefings.append({
                                "id": f"GDELT-LIVE-{i}",
                                "title": title,
                                "summary": f"Live GDELT threat intelligence: {title}",
                                "classification": cls_label,
                                "severity": severity,
                                "clearance_level": lvl,
                                "source": domain,
                                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                                "expires_in": 300 + i * 60,
                                "url": url,
                                "redacted_content": f"Source [{domain}] reports [REDACTED] threat event. Reference: {url[:60]}",
                                "tags": ["live", "gdelt", "threat"]
                            })
            except Exception as gdelt_err:
                logger.warning(f"[DarkIntel] GDELT live fallback failed: {gdelt_err}")

        # ── Filter by clearance ───────────────────────────────────────────────
        if clearance and clearance.upper() != "ALL":
            target_clearance = clearance.upper()
            if target_clearance.startswith("L-"):
                num_map = {"2": "LEVEL 2 (OPERATOR)", "3": "LEVEL 3 (ANALYST)",
                           "4": "LEVEL 4 (DIRECTOR)", "5": "LEVEL 5 (ADMIN)"}
                num = target_clearance.split("-")[1].split()[0]
                target_clearance = num_map.get(num, target_clearance)
            briefings = [b for b in briefings if b["clearance_level"] == target_clearance]

        return briefings

