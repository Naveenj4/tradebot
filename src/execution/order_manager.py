"""
src/execution/order_manager.py
Idempotent order execution and lifecycle management.
Places initial exchange SL upon entry fill and modifies it dynamically during trailing.
"""
from typing import Optional
from decimal import Decimal
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.brokers.base import IBrokerAdapter
from src.brokers.models import (
    BrokerOrderRequest, BrokerOrderType,
    BrokerOrderSide, BrokerOrderStatus
)
from src.storage.models import Order, OrderStatus
from src.storage.repository import OrderRepository

logger = logging.getLogger("TradeBot.OrderManager")

class OrderExecutionManager:
    def __init__(self, broker: IBrokerAdapter):
        self.broker = broker
        self.active_entry_order_id: Optional[str] = None
        self.active_sl_order_id: Optional[str] = None
        self.is_position_open = False

    async def execute_entry(
        self,
        session: AsyncSession,
        trading_date: str,
        symbol: str,
        quantity: int,
        order_type_str: str,
        limit_price: Optional[Decimal],
        buffer_points: Decimal = Decimal("0.50")
    ) -> Optional[str]:
        """
        Submits entry order with strict idempotency key: {trading_date}_ENTRY_{symbol}.
        """
        idempotency_key = f"{trading_date}_ENTRY_{symbol}"
        
        # Check if already submitted in DB
        existing = await OrderRepository.get_order_by_idempotency_key(session, idempotency_key)
        if existing:
            logger.warning(f"Idempotency Guard: Order with key {idempotency_key} already exists! Skipping.")
            return existing.broker_order_id

        # Determine order price
        order_type = BrokerOrderType.LIMIT if order_type_str == "LIMIT_BUFFER" else BrokerOrderType.MARKET
        final_limit_price = (limit_price + buffer_points) if (order_type == BrokerOrderType.LIMIT and limit_price) else None

        req = BrokerOrderRequest(
            tradingsymbol=symbol,
            exchange="NFO",
            transaction_type=BrokerOrderSide.BUY,
            quantity=quantity,
            order_type=order_type,
            price=final_limit_price,
            tag="tradebot_entry"
        )

        db_order = Order(
            idempotency_key=idempotency_key,
            trading_date=trading_date,
            instrument_symbol=symbol,
            order_purpose="ENTRY",
            side="BUY",
            quantity=quantity,
            order_type=order_type_str,
            limit_price=final_limit_price,
            status="SUBMITTED"
        )
        saved_order = await OrderRepository.save_order(session, db_order)

        res = await self.broker.place_order(req)
        if res.status in (BrokerOrderStatus.OPEN, BrokerOrderStatus.COMPLETE):
            self.active_entry_order_id = res.order_id
            self.is_position_open = True
            await OrderRepository.update_order_status(
                session,
                order_id=saved_order.id,
                status="FILLED" if res.status == BrokerOrderStatus.COMPLETE else "SUBMITTED",
                broker_order_id=res.order_id
            )
            logger.info(f"Entry order placed successfully: {res.order_id}")
            return res.order_id
        else:
            await OrderRepository.update_order_status(
                session,
                order_id=saved_order.id,
                status="REJECTED",
                error_msg=res.message
            )
            logger.error(f"Entry order rejected: {res.message}")
            return None

    async def place_exchange_stop_loss(
        self,
        session: AsyncSession,
        trading_date: str,
        symbol: str,
        quantity: int,
        trigger_sl_price: Decimal,
        limit_buffer: Decimal = Decimal("1.0")
    ) -> Optional[str]:
        """
        Places exchange-side SL-Limit order to protect capital against network disconnects.
        """
        idempotency_key = f"{trading_date}_SL_{symbol}"
        limit_price = trigger_sl_price - limit_buffer  # Limit protection buffer below trigger

        req = BrokerOrderRequest(
            tradingsymbol=symbol,
            exchange="NFO",
            transaction_type=BrokerOrderSide.SELL,
            quantity=quantity,
            order_type=BrokerOrderType.SL_LIMIT,
            price=limit_price,
            trigger_price=trigger_sl_price,
            tag="tradebot_sl"
        )

        db_order = Order(
            idempotency_key=idempotency_key,
            trading_date=trading_date,
            instrument_symbol=symbol,
            order_purpose="STOP_LOSS",
            side="SELL",
            quantity=quantity,
            order_type="SL_LIMIT",
            limit_price=limit_price,
            trigger_price=trigger_sl_price,
            status="SUBMITTED"
        )
        saved_order = await OrderRepository.save_order(session, db_order)

        res = await self.broker.place_order(req)
        if res.status in (BrokerOrderStatus.OPEN, BrokerOrderStatus.COMPLETE):
            self.active_sl_order_id = res.order_id
            await OrderRepository.update_order_status(
                session,
                order_id=saved_order.id,
                status="TRIGGERED" if res.status == BrokerOrderStatus.OPEN else "FILLED",
                broker_order_id=res.order_id
            )
            logger.info(f"Exchange SL order placed: {res.order_id} at Trigger={trigger_sl_price}")
            return res.order_id
        return None

    async def modify_exchange_stop_loss(
        self,
        new_sl_price: Decimal,
        limit_buffer: Decimal = Decimal("1.0")
    ) -> bool:
        """
        Dynamically modifies the exchange-side SL order as price moves in our favor.
        """
        if not self.active_sl_order_id:
            logger.warning("No active SL order ID found to modify.")
            return False

        new_limit = new_sl_price - limit_buffer
        success = await self.broker.modify_order(
            order_id=self.active_sl_order_id,
            price=new_limit,
            trigger_price=new_sl_price
        )
        if success:
            logger.info(f"Dynamically ratcheted exchange SL {self.active_sl_order_id} -> Trigger: {new_sl_price}")
        return success

    async def cancel_pending_entry(self) -> bool:
        """Called at 09:20:00 IST if order was not filled."""
        if self.active_entry_order_id and not self.is_position_open:
            return await self.broker.cancel_order(self.active_entry_order_id)
        return False

