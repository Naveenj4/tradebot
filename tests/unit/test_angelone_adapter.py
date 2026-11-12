"""
tests/unit/test_angelone_adapter.py
Unit tests for Angel One SmartAPI adapter and TOTP authenticator.
"""
from decimal import Decimal
from src.brokers.angelone.auth import AngelOneAuthenticator
from src.brokers.angelone.adapter import AngelOneBrokerAdapter
from src.brokers.models import (
    BrokerOrderRequest, BrokerOrderSide, BrokerOrderType, BrokerOrderStatus
)

def test_angelone_totp_generation():
    test_secret = "JBSWY3DPEHPK3PXP"
    auth = AngelOneAuthenticator(
        api_key="test_api_key",
        client_id="A123456",
        password="test_password",
        totp_secret=test_secret
    )
    totp = auth.generate_totp()
    assert len(totp) == 6
    assert totp.isdigit()

def test_angelone_order_type_mappings():
    adapter = AngelOneBrokerAdapter(
        api_key="test_key",
        client_id="A123456",
        password="test_pass",
        totp_secret="JBSWY3DPEHPK3PXP"
    )

    assert adapter.ORDER_TYPE_MAP[BrokerOrderType.MARKET] == "MARKET"
    assert adapter.ORDER_TYPE_MAP[BrokerOrderType.LIMIT] == "LIMIT"
    assert adapter.ORDER_TYPE_MAP[BrokerOrderType.SL_LIMIT] == "STOPLOSS_LIMIT"
    assert adapter.ORDER_TYPE_MAP[BrokerOrderType.SL_MARKET] == "STOPLOSS_MARKET"

    assert adapter.SIDE_MAP[BrokerOrderSide.BUY] == "BUY"
    assert adapter.SIDE_MAP[BrokerOrderSide.SELL] == "SELL"

    assert adapter.VARIETY_MAP[BrokerOrderType.LIMIT] == "NORMAL"
    assert adapter.VARIETY_MAP[BrokerOrderType.SL_LIMIT] == "STOPLOSS"

def test_angelone_place_order_validation():
    adapter = AngelOneBrokerAdapter(
        api_key="test_key",
        client_id="A123456",
        password="test_pass",
        totp_secret="JBSWY3DPEHPK3PXP"
    )

    req = BrokerOrderRequest(
        tradingsymbol="NIFTY26NOV25400CE",
        exchange="NFO",
        transaction_type=BrokerOrderSide.BUY,
        quantity=50,
        order_type=BrokerOrderType.LIMIT,
        price=Decimal("120.00")
    )

    coro = adapter.place_order(req)
    try:
        coro.send(None)
    except StopIteration as e:
        res = e.value
        assert res.status == BrokerOrderStatus.REJECTED
        assert "not initialised" in res.message.lower()
