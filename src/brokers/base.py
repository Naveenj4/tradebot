"""
src/brokers/base.py
Abstract base class definition for broker adapters.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from decimal import Decimal
from src.brokers.models import (
    BrokerOrderRequest, BrokerOrderResponse,
    BrokerPosition, InstrumentInfo
)

class IBrokerAdapter(ABC):
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticates session with broker via API keys or automated TOTP."""
        pass

    @abstractmethod
    async def get_instruments(self, exchange: str = "NFO") -> List[InstrumentInfo]:
        """Fetches and caches daily master instrument dump from broker."""
        pass

    @abstractmethod
    async def get_available_margin(self) -> Decimal:
        """Retrieves free cash / available trading margin in INR."""
        pass

    @abstractmethod
    async def place_order(self, request: BrokerOrderRequest) -> BrokerOrderResponse:
        """Submits an order to the broker with validation and error handling."""
        pass

    @abstractmethod
    async def modify_order(
        self,
        order_id: str,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        quantity: Optional[int] = None
    ) -> bool:
        """Modifies an existing open order (e.g. dynamic trailing SL)."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancels an open pending or trigger order."""
        pass

    @abstractmethod
    async def get_positions(self) -> List[BrokerPosition]:
        """Fetches active day positions from the broker."""
        pass

