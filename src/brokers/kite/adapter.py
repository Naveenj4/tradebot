"""
src/brokers/kite/adapter.py
Zerodha Kite Connect v3 REST adapter conforming to IBrokerAdapter.
"""
from typing import List, Dict, Optional
from decimal import Decimal
import logging
from kiteconnect import KiteConnect
from src.brokers.base import IBrokerAdapter
from src.brokers.models import (
    BrokerOrderRequest, BrokerOrderResponse,
    BrokerOrderStatus, BrokerOrderSide, BrokerOrderType,
    BrokerPosition, InstrumentInfo
)
from src.brokers.kite.auth import KiteAuthenticator

logger = logging.getLogger("TradeBot.KiteAdapter")

class KiteBrokerAdapter(IBrokerAdapter):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        user_id: str,
        password: str,
        totp_key: str
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        self.auth = KiteAuthenticator(api_key, api_secret, user_id, password, totp_key)
        self.access_token: Optional[str] = None
        self._instruments_cache: List[InstrumentInfo] = []

    async def authenticate(self) -> bool:
        token = await self.auth.get_access_token_headless()
        if token:
            self.access_token = token
            self.kite.set_access_token(token)
            logger.info("Successfully authenticated Kite Connect session.")
            return True
        logger.error("Kite authentication failed.")
        return False

    async def get_instruments(self, exchange: str = "NFO") -> List[InstrumentInfo]:
        if self._instruments_cache:
            return self._instruments_cache

        try:
            raw_instruments = self.kite.instruments(exchange)
            parsed = []
            for item in raw_instruments:
                parsed.append(InstrumentInfo(
                    instrument_token=item["instrument_token"],
                    exchange_token=item["exchange_token"],
                    tradingsymbol=item["tradingsymbol"],
                    name=item["name"],
                    last_price=Decimal(str(item.get("last_price", 0.0))),
                    expiry=item.get("expiry"),
                    strike=Decimal(str(item.get("strike", 0.0))) if item.get("strike") else None,
                    tick_size=Decimal(str(item.get("tick_size", 0.05))),
                    lot_size=item.get("lot_size", 1),
                    instrument_type=item.get("instrument_type", ""),
                    segment=item.get("segment", ""),
                    exchange=item.get("exchange", exchange)
                ))
            self._instruments_cache = parsed
            return self._instruments_cache
        except Exception as e:
            logger.warning(f"Could not load live instruments from Kite ({e}); using cached/fallback.")
            return []

    async def get_available_margin(self) -> Decimal:
        try:
            margins = self.kite.margins(segment="equity")
            net = margins.get("net", 0.0)
            return Decimal(str(net))
        except Exception as e:
            logger.error(f"Error fetching margins from Kite: {e}")
            return Decimal("0.0")

    async def place_order(self, request: BrokerOrderRequest) -> BrokerOrderResponse:
        order_type_map = {
            BrokerOrderType.MARKET: self.kite.ORDER_TYPE_MARKET,
            BrokerOrderType.LIMIT: self.kite.ORDER_TYPE_LIMIT,
            BrokerOrderType.SL_LIMIT: self.kite.ORDER_TYPE_SL,
            BrokerOrderType.SL_MARKET: self.kite.ORDER_TYPE_SLM,
        }
        side_map = {
            BrokerOrderSide.BUY: self.kite.TRANSACTION_TYPE_BUY,
            BrokerOrderSide.SELL: self.kite.TRANSACTION_TYPE_SELL,
        }

        try:
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=request.exchange,
                tradingsymbol=request.tradingsymbol,
                transaction_type=side_map[request.transaction_type],
                quantity=request.quantity,
                product=self.kite.PRODUCT_MIS,
                order_type=order_type_map[request.order_type],
                price=float(request.price) if request.price else None,
                trigger_price=float(request.trigger_price) if request.trigger_price else None,
                tag=request.tag or "tradebot"
            )
            return BrokerOrderResponse(
                order_id=str(order_id),
                status=BrokerOrderStatus.OPEN,
                message="Submitted to Kite"
            )
        except Exception as e:
            logger.error(f"Kite order placement failed: {e}")
            return BrokerOrderResponse(
                order_id="",
                status=BrokerOrderStatus.REJECTED,
                message=str(e)
            )

    async def modify_order(
        self,
        order_id: str,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        quantity: Optional[int] = None
    ) -> bool:
        try:
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                price=float(price) if price else None,
                trigger_price=float(trigger_price) if trigger_price else None,
                quantity=quantity
            )
            return True
        except Exception as e:
            logger.error(f"Failed to modify order {order_id} on Kite: {e}")
            return False

    async def cancel_order(self, order_id: str) -> bool:
        try:
            self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id} on Kite: {e}")
            return False

    async def get_positions(self) -> List[BrokerPosition]:
        try:
            res = self.kite.positions()
            day_positions = res.get("day", [])
            output = []
            for pos in day_positions:
                output.append(BrokerPosition(
                    tradingsymbol=pos["tradingsymbol"],
                    exchange=pos["exchange"],
                    instrument_token=pos["instrument_token"],
                    quantity=pos["quantity"],
                    average_price=Decimal(str(pos.get("average_price", 0.0))),
                    last_price=Decimal(str(pos.get("last_price", 0.0))),
                    pnl=Decimal(str(pos.get("pnl", 0.0)))
                ))
            return output
        except Exception as e:
            logger.error(f"Failed to fetch positions from Kite: {e}")
            return []

