import asyncio
import random
import uuid
from datetime import datetime
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker
from models.db_models import EntityModel

fake = Faker()

DOMAINS = ["financial", "healthcare", "iot", "social"]

# Pre-defined tickers for fake entities to prevent infinite loops
FAKE_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "JPM", "VTI",
                "KO", "PEP", "DIS", "IBM", "ORCL", "ADBE", "CRM", "AMD", "INTC", "CSCO",
                "QCOM", "TXN", "NKE", "SBUX", "MCD", "WMT", "TGT", "HD", "LOW", "COST"]

class EntityRegistry:
    """
    In-memory entity registry backed by the PostgreSQL entities table.
    On first startup the table is empty, so 50 fake entities are generated
    and persisted. On subsequent startups the existing rows are loaded instead,
    giving a stable entity pool across restarts.
    In production, this would query PRAGMA's knowledge graph.
    """

    def __init__(self):
        self.entities: dict[str, dict] = {}
        # Async bootstrap is called explicitly from main.py after init_db().
        self._bootstrap_lock = asyncio.Lock()
        self._is_bootstrapped = False

    async def _bootstrap_async(self):
        """Load entities from DB if they exist, otherwise seed 50 fake ones."""
        # Prevent multiple simultaneous bootstrap attempts
        async with self._bootstrap_lock:
            if self._is_bootstrapped:
                return
            
            from config import USE_REAL_DATA
            
            if USE_REAL_DATA:
                from models.commerce import CompanyModel
                from sqlalchemy.orm import selectinload
                async with async_session_maker() as session:
                    try:
                        stmt = select(CompanyModel).options(
                            selectinload(CompanyModel.financial_metrics),
                            selectinload(CompanyModel.job_postings)
                        )
                        result = await session.execute(stmt)
                        companies = result.scalars().all()
                        if companies:
                            for c in companies:
                                latest_metrics = c.financial_metrics[-1] if c.financial_metrics else None
                                rev = latest_metrics.revenue if latest_metrics else 0.0
                                sec = (c.sector or '').lower()
                                if 'financial' in sec or 'bank' in sec or 'insurance' in sec:
                                    domain = 'financial'
                                elif 'health' in sec or 'pharma' in sec or 'bio' in sec or 'medical' in sec or 'life sciences' in sec or 'clinical' in sec:
                                    domain = 'healthcare'
                                elif any(x in sec for x in ['tech', 'software', 'hardware', 'iot', 'energy', 'industrial', 'utility', 'utilities', 'semiconductor', 'telecom', 'material', 'materials', 'communication']):
                                    domain = 'iot'
                                else:
                                    domain = 'social'
                                    
                                self.entities[c.id] = {
                                    "id": c.id,
                                    "name": c.legal_name,
                                    "domain": domain,
                                    "status": "stable",
                                    "entropy": 0.5,
                                    "event_count": len(c.job_postings),
                                    "alert_count": 0,
                                    "ticker": c.ticker,
                                    "revenue": rev
                                }
                            self._is_bootstrapped = True
                            return
                    except Exception as e:
                        print(f"[ENTITY REGISTRY] Failed to load real companies: {e}")

            async with async_session_maker() as session:
                # Check whether the table already has rows
                result = await session.execute(select(EntityModel).limit(1))
                existing = result.scalars().first()

                if existing:
                    # Table is populated — load all rows into the in-memory registry
                    all_rows = await session.execute(select(EntityModel))
                    for row in all_rows.scalars().all():
                        meta = row.metadata_json or {}
                        # ✅ FIX: Generate a ticker for entities if missing
                        ticker = meta.get("ticker")
                        if not ticker:
                            # Generate a deterministic ticker from the entity name
                            name_clean = row.name.replace(" ", "").upper()[:4]
                            ticker = name_clean if len(name_clean) >= 3 else f"{name_clean}X"
                        
                        self.entities[row.id] = {
                            "id": row.id,
                            "name": row.name,
                            "domain": row.domain,
                            "status": row.status,
                            "entropy": row.entropy,
                            "event_count": meta.get("event_count", 0),
                            "alert_count": meta.get("alert_count", 0),
                            "ticker": ticker,  # ✅ Added ticker
                            "revenue": meta.get("revenue", random.uniform(10, 500)),  # ✅ Added revenue
                        }
                    self._is_bootstrapped = True
                    return

                # Table is empty — generate 50 fake entities and persist them
                for i in range(50):
                    domain = random.choice(DOMAINS)
                    eid = f"E-{uuid.uuid4().hex[:8].upper()}"
                    entropy = round(random.uniform(0.1, 1.5), 4)
                    
                    # ✅ FIX: Generate a realistic ticker
                    ticker = random.choice(FAKE_TICKERS)
                    if i < len(FAKE_TICKERS):
                        ticker = FAKE_TICKERS[i % len(FAKE_TICKERS)]
                    else:
                        # Generate a random ticker for extra entities
                        ticker = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
                    
                    name = fake.company()
                    revenue = round(random.uniform(10, 1000), 2)

                    entity_dict = {
                        "id": eid,
                        "name": name,
                        "domain": domain,
                        "status": "stable",
                        "entropy": entropy,
                        "event_count": 0,
                        "alert_count": 0,
                        "ticker": ticker,  # ✅ Added ticker
                        "revenue": revenue,  # ✅ Added revenue
                    }
                    self.entities[eid] = entity_dict

                    # Persist to DB with ticker in metadata
                    session.add(EntityModel(
                        id=eid,
                        name=name,
                        domain=domain,
                        status="stable",
                        entropy=entropy,
                        metadata_json={
                            "event_count": 0,
                            "alert_count": 0,
                            "ticker": ticker,
                            "revenue": revenue
                        },
                    ))

                await session.commit()
                self._is_bootstrapped = True

    def get_random_entity(self) -> dict:
        return random.choice(list(self.entities.values()))

    def get_all(self) -> list:
        """Return all entities with a limit to prevent infinite loops."""
        # ✅ FIX: Limit to first 100 entities to prevent overwhelming
        return list(self.entities.values())[:100]

    def get_by_id(self, entity_id: str) -> dict | None:
        return self.entities.get(entity_id)

    def get_by_ticker(self, ticker: str) -> dict | None:
        """Find an entity by its ticker symbol."""
        for entity in self.entities.values():
            if entity.get("ticker", "").upper() == ticker.upper():
                return entity
        return None

    def search(self, query: str, limit: int = 20) -> list:
        """Search entities by name or ticker."""
        query_lower = query.lower()
        results = []
        for entity in self.entities.values():
            name = entity.get("name", "").lower()
            ticker = entity.get("ticker", "").lower()
            if query_lower in name or query_lower in ticker:
                results.append(entity)
                if len(results) >= limit:
                    break
        return results

    async def _persist_entity_state(self, entity_id: str):
        """Write the current in-memory entropy + status back to the DB row."""
        try:
            async with async_session_maker() as session:
                result = await session.execute(
                    select(EntityModel).where(EntityModel.id == entity_id)
                )
                row = result.scalars().first()
                if row:
                    row.status = self.entities[entity_id]["status"]
                    row.entropy = self.entities[entity_id]["entropy"]
                    row.last_updated = datetime.utcnow()
                    await session.commit()
        except Exception as e:
            print(f"[ENTITY] DB state persist failed for {entity_id}: {e}")

    def update_entropy(self, entity_id: str, entropy: float, alert: bool, z_score: float = 0.0):
        if entity_id in self.entities:
            self.entities[entity_id]["entropy"] = entropy
            self.entities[entity_id]["event_count"] += 1
            if alert:
                self.entities[entity_id]["alert_count"] += 1
                self.entities[entity_id]["status"] = "pre-transition"
            elif self.entities[entity_id].get("status") == "pre-transition" and entropy < 0.8 and abs(z_score) < 1.0:
                self.entities[entity_id]["status"] = "stable"
            elif entropy < 1.5:
                self.entities[entity_id]["status"] = "stable"
            asyncio.create_task(self._persist_entity_state(entity_id))

    def get_stats(self) -> dict:
        """Get registry statistics."""
        total = len(self.entities)
        by_domain = {}
        by_status = {}
        for entity in self.entities.values():
            domain = entity.get("domain", "unknown")
            status = entity.get("status", "unknown")
            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        return {
            "total_entities": total,
            "by_domain": by_domain,
            "by_status": by_status,
            "is_bootstrapped": self._is_bootstrapped
        }


# Singleton instance used across the app.
# _bootstrap_async() is awaited from main.py after init_db() completes.
entity_registry = EntityRegistry()