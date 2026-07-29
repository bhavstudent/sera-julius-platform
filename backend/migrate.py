import asyncio
from database import engine, Base
from sqlalchemy import text

async def run_migration():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE security_engagements ADD COLUMN IF NOT EXISTS auto_approved BOOLEAN DEFAULT FALSE;"))
        await conn.execute(text("ALTER TABLE security_engagements ADD COLUMN IF NOT EXISTS auto_approved_by VARCHAR;"))
        await conn.execute(text("ALTER TABLE security_engagements ADD COLUMN IF NOT EXISTS auto_approved_at TIMESTAMP;"))
    print("Database migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
