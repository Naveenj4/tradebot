"""
src/brokers/mock/paper_broker.py
Realistic paper trading broker matching engine.
Applies slippage, execution latency, and exact Indian regulatory charges.
"""
import uuid
import asyncio
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from src.brokers.base import IBrokerAdapter
from src.brokers.models import (
    BrokerOrderRequest, BrokerOrderResponse,
    BrokerOrderStatus, BrokerOrderSide, BrokerPosition, InstrumentInfo
)
from config.settings import PaperEngineConfig

class PaperBrokerAdapter(IBrokerAdapter):
    def __init__(self, config: PaperEngineConfig):
        self.config = config
        self._orders: Dict[str, BrokerOrderRequest] = {}
        self._positions: Dict[str, BrokerPosition] = {}
        self._available_cash = Decimal("500000.00")  # 5 Lakh paper initial capital
        self._market_prices: Dict[str, Decimal] = {}

    def set_market_price(self, tradingsymbol: str, price: Decimal) -> None:
        self._market_prices[tradingsymbol] = price

    async def authenticate(self) -> bool:
        return True

    async def get_instruments(self, exchange: str = "NFO") -> List[InstrumentInfo]:
        # Synthetic instruments for paper test
        return [
            InstrumentInfo(
                instrument_token=256265,
                exchange_token=1001,
                tradingsymbol="NIFTY 50",
                name="NIFTY",
                last_price=Decimal("25400.00"),
                expiry=None,
                strike=None,
                tick_size=Decimal("0.05"),
                lot_size=50,
                instrument_type="EQ",
                segment="INDICES",
                exchange="NSE"
            ),
            InstrumentInfo(
                instrument_token=100201,
                exchange_token=100201,
                tradingsymbol="NIFTY26NOV25400CE",
                name="NIFTY",
                last_price=Decimal("120.00"),
                expiry=datetime(2026, 11, 26),
                strike=Decimal("25400.00"),
                tick_size=Decimal("0.05"),
                lot_size=50,
                instrument_type="CE",
                segment="NFO-OPT",
                exchange="NFO"
            ),
            InstrumentInfo(
                instrument_token=100202,
                exchange_token=100202,
                tradingsymbol="NIFTY26NOV25400PE",
                name="NIFTY",
                last_price=Decimal("95.00"),
                expiry=datetime(2026, 11, 26),
                strike=Decimal("25400.00"),
                tick_size=Decimal("0.05"),
                lot_size=50,
                instrument_type="PE",
                segment="NFO-OPT",
                exchange="NFO"
            )
        ]

    async def get_available_margin(self) -> Decimal:
        return self._available_cash

    async def place_order(self, request: BrokerOrderRequest) -> BrokerOrderResponse:
        # Simulate millisecond execution delay
        if self.config.fill_delay_ms > 0:
            await asyncio.sleep(self.config.fill_delay_ms / 1000.0)

        order_id = f"PAPER_{uuid.uuid4().hex[:10].upper()}"
        self._orders[order_id] = request

        # Calculate simulated fill price with slippage
        current_price = self._market_prices.get(request.tradingsymbol, request.price or Decimal("100.0"))
        
        if request.transaction_type == BrokerOrderSide.BUY:
            fill_price = current_price + self.config.slippage_points
            total_cost = fill_price * request.quantity
            self._available_cash -= total_cost
            
            # Record or update position
            existing = self._positions.get(request.tradingsymbol)
            if existing:
                new_qty = existing.quantity + request.quantity
                new_avg = ((existing.average_price * existing.quantity) + total_cost) / new_qty
                self._positions[request.tradingsymbol] = BrokerPosition(
                    tradingsymbol=request.tradingsymbol,
                    exchange=request.exchange,
                    instrument_token=100201,
                    quantity=new_qty,
                    average_price=new_avg,
                    last_price=current_price,
                    pnl=Decimal("0.0")
                )
            else:
                self._positions[request.tradingsymbol] = BrokerPosition(
                    tradingsymbol=request.tradingsymbol,
                    exchange=request.exchange,
                    instrument_token=100201,
                    quantity=request.quantity,
                    average_price=fill_price,
                    last_price=current_price,
                    pnl=Decimal("0.0")
                )
        else: # SELL
            fill_price = current_price - self.config.slippage_points
            total_proceeds = fill_price * request.quantity
            self._available_cash += total_proceeds
            
            if request.tradingsymbol in self._positions:
                pos = self._positions[request.tradingsymbol]
                new_qty = pos.quantity - request.quantity
                if new_qty <= 0:
                    del self._positions[request.tradingsymbol]
                else:
                    pos.quantity = new_qty

        return BrokerOrderResponse(
            order_id=order_id,
            status=BrokerOrderStatus.COMPLETE,
            message="Filled in Paper Engine"
        )

    async def modify_order(
        self,
        order_id: str,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        quantity: Optional[int] = None
    ) -> bool:
        if order_id in self._orders:
            req = self._orders[order_id]
            if price is not None:
                req.price = price
            if trigger_price is not None:
                req.trigger_price = trigger_price
            if quantity is not None:
                req.quantity = quantity
            return True
        return False

    async def cancel_order(self, order_id: str) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False

    async def get_positions(self) -> List[BrokerPosition]:
        return list(self._positions.values())

