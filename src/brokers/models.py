"""
src/brokers/models.py
Canonical domain models for broker interactions, independent of specific broker APIs.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime
from enum import Enum

class BrokerOrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL_LIMIT = "SL"
    SL_MARKET = "SL-M"

class BrokerOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class BrokerOrderStatus(str, Enum):
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class InstrumentInfo:
    instrument_token: int
    exchange_token: int
    tradingsymbol: str
    name: str
    last_price: Decimal
    expiry: Optional[datetime]
    strike: Optional[Decimal]
    tick_size: Decimal
    lot_size: int
    instrument_type: str  # CE, PE, EQ, FUT
    segment: str
    exchange: str

@dataclass
class BrokerOrderRequest:
    tradingsymbol: str
    exchange: str
    transaction_type: BrokerOrderSide
    quantity: int
    order_type: BrokerOrderType
    price: Optional[Decimal] = None
    trigger_price: Optional[Decimal] = None
    tag: Optional[str] = None

@dataclass
class BrokerOrderResponse:
    order_id: str
    status: BrokerOrderStatus
    message: Optional[str] = None

@dataclass
class BrokerPosition:
    tradingsymbol: str
    exchange: str
    instrument_token: int
    quantity: int
    average_price: Decimal
    last_price: Decimal
    pnl: Decimal

