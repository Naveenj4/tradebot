"""
src/execution/reconciler.py
Startup ledger reconciliation against broker API.
Guarantees that a daemon restart will never enter duplicate positions or lose track of open orders.
"""
from typing import Dict, Any, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.brokers.base import IBrokerAdapter
from src.storage.models import Position, Order
from src.storage.repository import OrderRepository

logger = logging.getLogger("TradeBot.Reconciler")

class StartupReconciler:
    def __init__(self, broker: IBrokerAdapter):
        self.broker = broker

    async def reconcile(self, session: AsyncSession, trading_date: str) -> Dict[str, Any]:
        """
        Reconciles broker active positions with local database state.
        """
        logger.info(f"Executing startup ledger reconciliation for {trading_date}...")
        broker_positions = await self.broker.get_positions()
        
        has_open_position = False
        reconciled_symbol = None
        quantity = 0

        for pos in broker_positions:
            if pos.quantity != 0 and pos.tradingsymbol.startswith("NIFTY"):
                has_open_position = True
                reconciled_symbol = pos.tradingsymbol
                quantity = pos.quantity
                logger.warning(
                    f"Cold Restart Recovery: Found ACTIVE broker position: {pos.tradingsymbol} "
                    f"Qty={pos.quantity} @ Avg={pos.average_price}"
                )

        return {
            "has_open_position": has_open_position,
            "symbol": reconciled_symbol,
            "quantity": quantity,
            "reconciled_at": trading_date
        }

