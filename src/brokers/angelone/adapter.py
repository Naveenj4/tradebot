"""
src/brokers/angelone/adapter.py
Angel One SmartAPI broker adapter conforming to IBrokerAdapter.

Angel One SmartAPI specifics:
  - Uses 'symboltoken' (string) instead of numeric instrument_token
  - Exchange values: 'NSE', 'NFO', 'BSE', 'MCX'
  - Product types: INTRADAY, DELIVERY, CARRYFORWARD, MARGIN, BO, AMO
  - Order types: MARKET, LIMIT, STOPLOSS_LIMIT, STOPLOSS_MARKET
  - Variety: NORMAL, STOPLOSS, AMO, ROBO
  - Duration: DAY, IOC
  - Instrument list is fetched via a separate OpenAPI JSON endpoint
"""
import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from src.brokers.base import IBrokerAdapter
from src.brokers.models import (
    BrokerOrderRequest,
    BrokerOrderResponse,
    BrokerOrderSide,
    BrokerOrderStatus,
    BrokerOrderType,
    BrokerPosition,
    InstrumentInfo,
)
from src.brokers.angelone.auth import AngelOneAuthenticator

logger = logging.getLogger("TradeBot.AngelOneAdapter")

# Angel One publishes the full instrument master as a JSON file
ANGEL_INSTRUMENT_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"


class AngelOneBrokerAdapter(IBrokerAdapter):
    """
    Full-featured Angel One SmartAPI adapter.
    Maps canonical BrokerOrderRequest/Response to Angel One's REST semantics.
    """

    # ---- Angel One enum mappings ----
    ORDER_TYPE_MAP: Dict[BrokerOrderType, str] = {
        BrokerOrderType.MARKET: "MARKET",
        BrokerOrderType.LIMIT: "LIMIT",
        BrokerOrderType.SL_LIMIT: "STOPLOSS_LIMIT",
        BrokerOrderType.SL_MARKET: "STOPLOSS_MARKET",
    }

    SIDE_MAP: Dict[BrokerOrderSide, str] = {
        BrokerOrderSide.BUY: "BUY",
        BrokerOrderSide.SELL: "SELL",
    }

    VARIETY_MAP: Dict[BrokerOrderType, str] = {
        BrokerOrderType.MARKET: "NORMAL",
        BrokerOrderType.LIMIT: "NORMAL",
        BrokerOrderType.SL_LIMIT: "STOPLOSS",
        BrokerOrderType.SL_MARKET: "STOPLOSS",
    }

    def __init__(
        self,
        api_key: str,
        client_id: str,
        password: str,
        totp_secret: str,
    ):
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret

        self.auth = AngelOneAuthenticator(api_key, client_id, password, totp_secret)
        self._smart_api = None  # Lazy-initialised SmartConnect instance
        self._jwt_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._feed_token: Optional[str] = None
        self._instruments_cache: List[InstrumentInfo] = []
        self._symbol_token_map: Dict[str, str] = {}  # tradingsymbol -> symboltoken

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    async def authenticate(self) -> bool:
        """Creates an Angel One session using SmartConnect + TOTP."""
        try:
            from SmartApi import SmartConnect

            self._smart_api = SmartConnect(api_key=self.api_key)
            jwt, refresh = self.auth.create_session(self._smart_api)

            if jwt and refresh:
                self._jwt_token = jwt
                self._refresh_token = refresh
                self._feed_token = self._smart_api.getfeedToken()
                logger.info(
                    f"Angel One authenticated. Client: {self.client_id}, "
                    f"Feed token: {'OK' if self._feed_token else 'N/A'}"
                )
                return True

            logger.error("Angel One authentication returned empty tokens.")
            return False

        except ImportError:
            logger.error(
                "smartapi-python package not installed. "
                "Run: pip install smartapi-python"
            )
            return False
        except Exception as e:
            logger.error(f"Angel One authentication failed: {e}", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Instruments
    # ------------------------------------------------------------------
    async def get_instruments(self, exchange: str = "NFO") -> List[InstrumentInfo]:
        """
        Downloads the Angel One OpenAPI instrument master JSON and caches it.
        Falls back to a local cached copy if the download fails.
        """
        if self._instruments_cache:
            return self._instruments_cache

        cache_path = Path("data") / "angel_instruments_cache.json"
        raw_data: list = []

        # Try downloading fresh
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(ANGEL_INSTRUMENT_URL)
                resp.raise_for_status()
                raw_data = resp.json()
                # Persist to local cache
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(raw_data), encoding="utf-8")
                logger.info(f"Downloaded {len(raw_data)} instruments from Angel One.")
        except Exception as e:
            logger.warning(f"Failed to download Angel One instruments ({e}); trying local cache.")
            if cache_path.exists():
                raw_data = json.loads(cache_path.read_text(encoding="utf-8"))
                logger.info(f"Loaded {len(raw_data)} instruments from local cache.")
            else:
                logger.error("No Angel One instrument cache available.")
                return []

        # Parse and filter by exchange
        parsed: List[InstrumentInfo] = []
        for item in raw_data:
            item_exchange = item.get("exch_seg", "")
            if item_exchange != exchange:
                continue

            symbol = item.get("symbol", "")
            name = item.get("name", "")
            token = item.get("token", "")
            strike_val = item.get("strike", "0")
            expiry_raw = item.get("expiry", "")
            lot_size = int(item.get("lotsize", "1") or "1")
            tick_size_val = item.get("tick_size", "0.05")
            inst_type = item.get("instrumenttype", "")

            # Parse expiry (Angel One format: '26NOV2026' or 'ddMMMYYYY')
            expiry_dt = None
            if expiry_raw:
                for fmt in ("%d%b%Y", "%Y-%m-%d"):
                    try:
                        expiry_dt = datetime.strptime(expiry_raw.upper(), fmt)
                        break
                    except ValueError:
                        continue

            # Map Angel One instrument types to our canonical types
            canon_type = inst_type  # OPTIDX -> option index
            if inst_type == "OPTIDX":
                # Determine CE or PE from the symbol suffix
                if symbol.upper().endswith("CE"):
                    canon_type = "CE"
                elif symbol.upper().endswith("PE"):
                    canon_type = "PE"
            elif inst_type == "FUTIDX":
                canon_type = "FUT"

            info = InstrumentInfo(
                instrument_token=int(token) if token else 0,
                exchange_token=int(token) if token else 0,
                tradingsymbol=symbol,
                name=name,
                last_price=Decimal("0.0"),
                expiry=expiry_dt,
                strike=Decimal(str(strike_val)) / Decimal("100") if strike_val else None,
                tick_size=Decimal(str(tick_size_val)),
                lot_size=lot_size,
                instrument_type=canon_type,
                segment=item_exchange,
                exchange=item_exchange,
            )
            parsed.append(info)
            self._symbol_token_map[symbol] = str(token)

        self._instruments_cache = parsed
        logger.info(f"Parsed {len(parsed)} {exchange} instruments from Angel One master.")
        return self._instruments_cache

    def get_symbol_token(self, tradingsymbol: str) -> Optional[str]:
        """Looks up the Angel One symboltoken for a given tradingsymbol."""
        return self._symbol_token_map.get(tradingsymbol)

    # ------------------------------------------------------------------
    # Margin
    # ------------------------------------------------------------------
    async def get_available_margin(self) -> Decimal:
        """Retrieves available funds / margin from Angel One."""
        if not self._smart_api:
            return Decimal("0.0")
        try:
            rms_data = self._smart_api.rmsLimit()
            if rms_data and rms_data.get("status"):
                net = rms_data["data"].get("net", "0")
                available = rms_data["data"].get("availablecash", net)
                return Decimal(str(available))
            return Decimal("0.0")
        except Exception as e:
            logger.error(f"Error fetching margin from Angel One: {e}")
            return Decimal("0.0")

    # ------------------------------------------------------------------
    # Order placement
    # ------------------------------------------------------------------
    async def place_order(self, request: BrokerOrderRequest) -> BrokerOrderResponse:
        """Places an order on Angel One SmartAPI."""
        if not self._smart_api:
            return BrokerOrderResponse(
                order_id="",
                status=BrokerOrderStatus.REJECTED,
                message="Angel One session not initialised. Call authenticate() first.",
            )

        symbol_token = self.get_symbol_token(request.tradingsymbol)
        if not symbol_token:
            return BrokerOrderResponse(
                order_id="",
                status=BrokerOrderStatus.REJECTED,
                message=f"Symbol token not found for {request.tradingsymbol}. Load instruments first.",
            )

        order_params = {
            "variety": self.VARIETY_MAP.get(request.order_type, "NORMAL"),
            "tradingsymbol": request.tradingsymbol,
            "symboltoken": symbol_token,
            "transactiontype": self.SIDE_MAP[request.transaction_type],
            "exchange": request.exchange,
            "ordertype": self.ORDER_TYPE_MAP[request.order_type],
            "producttype": "INTRADAY",  # MIS equivalent for options day-trading
            "duration": "DAY",
            "quantity": str(request.quantity),
        }

        if request.price is not None:
            order_params["price"] = str(float(request.price))
        else:
            order_params["price"] = "0"

        if request.trigger_price is not None:
            order_params["triggerprice"] = str(float(request.trigger_price))
        else:
            order_params["triggerprice"] = "0"

        if request.tag:
            order_params["ordertag"] = request.tag[:20]  # Angel One limit: 20 chars

        try:
            response = self._smart_api.placeOrder(order_params)
            if response:
                order_id = str(response)
                logger.info(
                    f"Angel One order placed: {order_id} | "
                    f"{request.transaction_type.value} {request.quantity} "
                    f"{request.tradingsymbol} @ {request.order_type.value}"
                )
                return BrokerOrderResponse(
                    order_id=order_id,
                    status=BrokerOrderStatus.OPEN,
                    message="Submitted to Angel One",
                )
            else:
                return BrokerOrderResponse(
                    order_id="",
                    status=BrokerOrderStatus.REJECTED,
                    message="Angel One returned empty order ID",
                )
        except Exception as e:
            logger.error(f"Angel One order placement failed: {e}", exc_info=True)
            return BrokerOrderResponse(
                order_id="",
                status=BrokerOrderStatus.REJECTED,
                message=str(e),
            )

    # ------------------------------------------------------------------
    # Order modification (for dynamic trailing SL)
    # ------------------------------------------------------------------
    async def modify_order(
        self,
        order_id: str,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        quantity: Optional[int] = None,
    ) -> bool:
        """Modifies an existing order on Angel One (e.g. trailing stop-loss ratchet)."""
        if not self._smart_api:
            logger.error("Cannot modify order: Angel One session not initialised.")
            return False

        modify_params: Dict = {
            "variety": "STOPLOSS",  # SL modifications always use STOPLOSS variety
            "orderid": order_id,
            "ordertype": "STOPLOSS_LIMIT",
            "duration": "DAY",
        }

        if price is not None:
            modify_params["price"] = str(float(price))
        if trigger_price is not None:
            modify_params["triggerprice"] = str(float(trigger_price))
        if quantity is not None:
            modify_params["quantity"] = str(quantity)

        try:
            result = self._smart_api.modifyOrder(modify_params)
            if result:
                logger.info(
                    f"Angel One order {order_id} modified: "
                    f"trigger={trigger_price}, price={price}"
                )
                return True
            logger.warning(f"Angel One modify returned falsy for order {order_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to modify Angel One order {order_id}: {e}")
            return False

    # ------------------------------------------------------------------
    # Order cancellation
    # ------------------------------------------------------------------
    async def cancel_order(self, order_id: str) -> bool:
        """Cancels an open or trigger-pending order on Angel One."""
        if not self._smart_api:
            return False
        try:
            # Try STOPLOSS variety first (SL orders), then NORMAL
            for variety in ("STOPLOSS", "NORMAL"):
                try:
                    result = self._smart_api.cancelOrder(order_id, variety)
                    if result:
                        logger.info(f"Angel One order {order_id} cancelled (variety={variety}).")
                        return True
                except Exception:
                    continue
            logger.warning(f"Could not cancel Angel One order {order_id} under any variety.")
            return False
        except Exception as e:
            logger.error(f"Failed to cancel Angel One order {order_id}: {e}")
            return False

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------
    async def get_positions(self) -> List[BrokerPosition]:
        """Fetches current day positions from Angel One."""
        if not self._smart_api:
            return []
        try:
            position_data = self._smart_api.position()
            if not position_data or not position_data.get("status"):
                return []

            positions_list = position_data.get("data", []) or []
            output: List[BrokerPosition] = []

            for pos in positions_list:
                net_qty = int(pos.get("netqty", 0))
                if net_qty == 0:
                    continue

                output.append(
                    BrokerPosition(
                        tradingsymbol=pos.get("tradingsymbol", ""),
                        exchange=pos.get("exchange", "NFO"),
                        instrument_token=int(pos.get("symboltoken", 0)),
                        quantity=net_qty,
                        average_price=Decimal(str(pos.get("averageprice", 0))),
                        last_price=Decimal(str(pos.get("ltp", 0))),
                        pnl=Decimal(str(pos.get("pnl", 0))),
                    )
                )
            return output
        except Exception as e:
            logger.error(f"Failed to fetch positions from Angel One: {e}")
            return []

    # ------------------------------------------------------------------
    # Logout / cleanup
    # ------------------------------------------------------------------
    async def logout(self) -> bool:
        """Terminates the Angel One session."""
        if not self._smart_api:
            return True
        try:
            self._smart_api.terminateSession(self.client_id)
            logger.info("Angel One session terminated.")
            return True
        except Exception as e:
            logger.warning(f"Angel One logout error: {e}")
            return False
