import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from config import DATABASE_URL

logger = logging.getLogger(__name__)

DB_URL = DATABASE_URL or ""
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_URL.startswith("postgresql://") and "+asyncpg" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Configure engine kwargs dynamically for production PostgreSQL vs SQLite
engine_kwargs = {"echo": False, "future": True}
if DB_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    })

try:
    engine = create_async_engine(DB_URL, **engine_kwargs)
except Exception as _e:
    logger.error(f"[DATABASE] Engine creation error: {_e}")
    engine = create_async_engine("sqlite+aiosqlite:///./sera_db.sqlite3", echo=False, future=True)

async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionLocal = async_session_maker
Base = declarative_base()

async def verify_db_connection() -> None:
    """
    Resilient connection check. Confirms DATABASE_URL is not empty,
    and attempts to connect with exponential backoff retries.
    """
    if not DATABASE_URL or not DATABASE_URL.strip():
        raise RuntimeError("DATABASE_URL is not configured. Check DATABASE_URL in your .env file.")
    
    try:
        url_obj = make_url(DATABASE_URL)
        redacted_url = url_obj.render_as_string(hide_password=True)
    except Exception:
        redacted_url = str(DATABASE_URL)
        
    max_retries = 2
    retry_delay = 1.0
    
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info(f"[DATABASE] Connected successfully to database at {redacted_url}")
            return
        except Exception as e:
            if attempt == max_retries:
                logger.warning(f"[DATABASE] Could not verify DB connection: {e}. Starting anyway.")
                return
            logger.warning(
                f"[DATABASE] Connection attempt {attempt}/{max_retries} failed. Retrying in {retry_delay}s... Error: {e}"
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2.0, 2.0)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables."""
    # Resilient check before creating tables
    try:
        await verify_db_connection()
    except Exception as e:
        logger.warning(f"[DATABASE] Remote DB check notice: {e}. Continuing with database initialization.")
    
    # ✅ FIXED: Import models with correct names
    from models.db_models import (
        EntityModel, 
        EventModel, 
        AlertModel, 
        PredictionModel, 
        EntityRelationshipModel, 
        ClaimModel, 
        ClaimChallengeModel, 
        TrackedQueryModel, 
        CitationResultModel
    )
    
    # ✅ CRITICAL FIX: Use correct class names from commerce.py
    from models.commerce import (
        CompanyModel,
        FinancialMetricsModel,    # ✅ Fixed: Added 's' at the end
        JobPostingsModel,         # ✅ Fixed: Added 's' at the end
        SearchTrendsModel,
        VesselMovementsModel,
        NewsEventsModel,
        GitHubActivityModel,
        IngestionLogModel,
        TickerPriorityCacheModel,
        HealthcareMetric,
        ExecutiveMovement
    )
    
    from models.claims import TrackedQuery, Claim, Evidence, Challenge
    from models.security import (
        SecurityEngagement, 
        SecurityFinding, 
        EngagementPhaseLog,
        STYXDetection,
        STYXNode,
        STYXReport
    )
    from models.user import UserModel
    from models.entities import ThreatActorModel, AssetModel
    
    # Run Table Schema Creation in a transaction block safely
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning(f"[DATABASE] Schema creation notice: {e}")
        
    # Run Alter table modifications gracefully
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE news_events ADD COLUMN IF NOT EXISTS tickers TEXT"))
    except Exception:
        pass

    # Sentiment columns migration for companies table
    for col_name, col_type in [
        ("news_sentiment", "FLOAT"),
        ("news_mentions", "INTEGER"),
        ("reddit_sentiment", "FLOAT"),
        ("reddit_mentions", "INTEGER")
    ]:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}"))
        except Exception:
            pass

    logger.info("[DATABASE] Database initialization complete.")

# ============================================================
# ✅ FIX: Add db export for routers
# ============================================================

# This is the missing export that routers/auth.py is trying to import
db = None  # Placeholder for database connection

# If using SQLAlchemy, you can also export the session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Export for backwards compatibility
async_session = async_session_maker