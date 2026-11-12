"""
tests/unit/test_conditions.py
Unit tests for parallel ConditionEngine with consecutive tick confirmation.
"""
from decimal import Decimal
from src.core.conditions import ConditionEngine, InstrumentSide, OppositeAction
from src.core.bias import BiasDirection

def test_ce_bullish_qualification_requires_two_ticks():
    ce_engine = ConditionEngine(
        instrument_side=InstrumentSide.CE,
        user_average=Decimal("100.00"),
        required_confirmations=2
    )
    ce_engine.set_open_price(Decimal("105.00")) # Open > Ref (100) -> Cond 1 TRUE

    # Tick 1: LTP > 100
    state1 = ce_engine.evaluate_tick(ltp=Decimal("102.50"), bias=BiasDirection.BULLISH)
    assert state1.cond1_passed is True
    assert state1.cond2_passed is True
    assert state1.consecutive_confirmations == 1
    assert state1.is_triggered is False

    # Tick 2: LTP still > 100 -> Triggers!
    state2 = ce_engine.evaluate_tick(ltp=Decimal("103.00"), bias=BiasDirection.BULLISH)
    assert state2.consecutive_confirmations == 2
    assert state2.is_triggered is True

def test_pe_opposite_in_bullish_is_skipped():
    pe_engine = ConditionEngine(
        instrument_side=InstrumentSide.PE,
        user_average=Decimal("80.00"),
        opposite_action=OppositeAction.SKIP
    )
    pe_engine.set_open_price(Decimal("85.00"))
    
    state = pe_engine.evaluate_tick(ltp=Decimal("90.00"), bias=BiasDirection.BULLISH)
    assert state.is_triggered is False
    assert "configured to SKIP" in state.reason

def test_pe_bearish_qualification():
    pe_engine = ConditionEngine(
        instrument_side=InstrumentSide.PE,
        user_average=Decimal("90.00"),
        required_confirmations=2
    )
    pe_engine.set_open_price(Decimal("95.00"))  # Open > Ref (90)

    # Tick 1
    s1 = pe_engine.evaluate_tick(ltp=Decimal("92.00"), bias=BiasDirection.BEARISH)
    assert s1.cond1_passed is True
    assert s1.cond2_passed is True
    assert s1.is_triggered is False

    # Tick 2
    s2 = pe_engine.evaluate_tick(ltp=Decimal("94.00"), bias=BiasDirection.BEARISH)
    assert s2.is_triggered is True

