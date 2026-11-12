"""
src/storage/repository.py
Database repository operations for settings versions, daily snapshots, orders, and logs.
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.models import (
    SettingsVersion, DailySnapshot, MarketOpenPrice,
    Order, Fill, Position, EventLog, KillSwitchLog
)

class SettingsRepository:
    @staticmethod
    async def get_latest_version(session: AsyncSession) -> Optional[SettingsVersion]:
        stmt = select(SettingsVersion).order_by(desc(SettingsVersion.version_number)).limit(1)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def create_new_version(
        session: AsyncSession,
        reference_spot: Decimal,
        reference_ce_avg: Decimal,
        reference_pe_avg: Decimal,
        lots: int,
        stop_loss_value: Decimal,
        target_value: Decimal,
        change_summary: str = "",
        created_by: str = "user"
    ) -> SettingsVersion:
        latest = await SettingsRepository.get_latest_version(session)
        new_version_num = (latest.version_number + 1) if latest else 1
        
        new_ver = SettingsVersion(
            version_number=new_version_num,
            reference_spot=reference_spot,
            reference_ce_avg=reference_ce_avg,
            reference_pe_avg=reference_pe_avg,
            lots=lots,
            stop_loss_value=stop_loss_value,
            target_value=target_value,
            change_summary=change_summary,
            created_by=created_by,
            is_active=True
        )
        session.add(new_ver)
        await session.commit()
        await session.refresh(new_ver)
        return new_ver

class DailySnapshotRepository:
    @staticmethod
    async def get_snapshot_for_date(session: AsyncSession, trading_date: str) -> Optional[DailySnapshot]:
        stmt = select(DailySnapshot).where(DailySnapshot.trading_date == trading_date)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def save_snapshot(session: AsyncSession, snapshot: DailySnapshot) -> DailySnapshot:
        session.add(snapshot)
        await session.commit()
        await session.refresh(snapshot)
        return snapshot

class OrderRepository:
    @staticmethod
    async def save_order(session: AsyncSession, order: Order) -> Order:
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def get_order_by_idempotency_key(session: AsyncSession, key: str) -> Optional[Order]:
        stmt = select(Order).where(Order.idempotency_key == key)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def update_order_status(
        session: AsyncSession,
        order_id: int,
        status: str,
        broker_order_id: Optional[str] = None,
        error_msg: Optional[str] = None
    ) -> None:
        values = {"status": status}
        if broker_order_id:
            values["broker_order_id"] = broker_order_id
        if error_msg:
            values["error_message"] = error_msg

        stmt = update(Order).where(Order.id == order_id).values(**values)
        await session.execute(stmt)
        await session.commit()

class EventLogger:
    @staticmethod
    async def log_event(
        session: AsyncSession,
        level: str,
        category: str,
        event_name: str,
        details: Optional[str] = None
    ) -> None:
        evt = EventLog(
            level=level,
            category=category,
            event_name=event_name,
            details=details
        )
        session.add(evt)
        await session.commit()

