"""
tests/unit/test_race_arbiter.py
Unit tests for RaceArbiter single-winner mutex.
"""
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from src.core.race_arbiter import RaceArbiter, ExecutionSignal
from src.core.conditions import InstrumentSide

def test_simultaneous_signals_allow_only_one_winner():
    arbiter = RaceArbiter()
    
    ce_signal = ExecutionSignal(
        instrument_side=InstrumentSide.CE,
        symbol="NIFTY26NOV25400CE",
        trigger_price=Decimal("120.00"),
        timestamp="09:16:02",
        reason="CE Conditions Qualified"
    )
    
    pe_signal = ExecutionSignal(
        instrument_side=InstrumentSide.PE,
        symbol="NIFTY26NOV25400PE",
        trigger_price=Decimal("95.00"),
        timestamp="09:16:02",
        reason="PE Conditions Qualified"
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        f_ce = executor.submit(arbiter.claim_sync, ce_signal)
        f_pe = executor.submit(arbiter.claim_sync, pe_signal)
        res_ce = f_ce.result()
        res_pe = f_pe.result()

    assert (res_ce is True and res_pe is False) or (res_pe is True and res_ce is False)
    assert arbiter.has_winner is True
    assert arbiter.winner is not None

def test_sealed_window_rejects_new_signals():
    arbiter = RaceArbiter()
    arbiter.seal_window()

    signal = ExecutionSignal(
        instrument_side=InstrumentSide.CE,
        symbol="NIFTY26NOV25400CE",
        trigger_price=Decimal("120.00"),
        timestamp="09:20:01",
        reason="Late trigger"
    )

    claimed = arbiter.claim_sync(signal)
    assert claimed is False
    assert arbiter.has_winner is False
