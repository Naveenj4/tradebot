"""
tests/unit/test_strike_resolver.py
Unit tests for StrikeResolver.
"""
from decimal import Decimal
from datetime import datetime, date
from src.data.strike_resolver import StrikeResolver
from src.brokers.models import InstrumentInfo

def test_atm_calculation():
    assert StrikeResolver.calculate_atm_strike(Decimal("25424.00")) == 25400
    assert StrikeResolver.calculate_atm_strike(Decimal("25426.00")) == 25450
    assert StrikeResolver.calculate_atm_strike(Decimal("25449.95")) == 25450
    assert StrikeResolver.calculate_atm_strike(Decimal("25400.00")) == 25400

def test_contract_resolution():
    mock_instruments = [
        InstrumentInfo(
            instrument_token=101, exchange_token=101, tradingsymbol="NIFTY26NOV25400CE",
            name="NIFTY", last_price=Decimal("120"), expiry=datetime(2026, 11, 26),
            strike=Decimal("25400"), tick_size=Decimal("0.05"), lot_size=50,
            instrument_type="CE", segment="NFO-OPT", exchange="NFO"
        ),
        InstrumentInfo(
            instrument_token=102, exchange_token=102, tradingsymbol="NIFTY26NOV25400PE",
            name="NIFTY", last_price=Decimal("95"), expiry=datetime(2026, 11, 26),
            strike=Decimal("25400"), tick_size=Decimal("0.05"), lot_size=50,
            instrument_type="PE", segment="NFO-OPT", exchange="NFO"
        )
    ]

    ce, pe = StrikeResolver.resolve_contracts(
        instruments=mock_instruments,
        underlying="NIFTY",
        spot_price=Decimal("25410.00"),
        strike_rule="ATM",
        today_date=date(2026, 11, 20)
    )

    assert ce is not None
    assert ce.tradingsymbol == "NIFTY26NOV25400CE"
    assert pe is not None
    assert pe.tradingsymbol == "NIFTY26NOV25400PE"

