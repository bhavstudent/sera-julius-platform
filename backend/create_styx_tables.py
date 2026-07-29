import asyncio
from database import async_session_maker
from sqlalchemy import text

async def create_tables():
    async with async_session_maker() as session:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS styx_detections (
                id TEXT PRIMARY KEY,
                network_scope TEXT NOT NULL,
                detection_time TIMESTAMP NOT NULL,
                device_ip TEXT NOT NULL,
                detection_pattern TEXT NOT NULL,
                severity TEXT NOT NULL,
                details TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        """))
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS styx_nodes (
                id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL UNIQUE,
                ip_address TEXT NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                infection_status TEXT NOT NULL,
                node_type TEXT NOT NULL,
                parent_node TEXT
            )
        """))
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS styx_reports (
                id TEXT PRIMARY KEY,
                network_scope TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                report_data JSON NOT NULL
            )
        """))
        await session.commit()
        print("✅ STYX tables created successfully in PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(create_tables())