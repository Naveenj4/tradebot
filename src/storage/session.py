"""
src/storage/session.py
Async database engine & session factory with SQLite WAL mode pragma support.
"""
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from config.settings import global_settings
from src.storage.models import Base

# Ensure data directory exists
Path("data").mkdir(parents=True, exist_ok=True)
Path("data/ticks").mkdir(parents=True, exist_ok=True)

# Build async engine
DATABASE_URL = global_settings.DATABASE_URL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Apply SQLite WAL and performance pragmas if using SQLite
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db() -> None:
    """Creates database tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for FastAPI / tasks."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

