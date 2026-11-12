"""
tests/unit/test_risk.py
Unit tests for dynamic trailing stop-loss ratcheting.
"""
from decimal import Decimal
from src.core.risk import DynamicPositionRiskManager

def test_dynamic_trailing_sl_ratchets_upward():
    rm = DynamicPositionRiskManager(
        entry_price=Decimal("100.00"),
        quantity=50,
        stop_loss_points=Decimal("20.00"),
        target_points=Decimal("40.00"),
        trailing_enabled=True,
        trailing_activation_points=Decimal("15.00"),
        trailing_step_points=Decimal("5.00")
    )

    assert rm.current_stop_loss == Decimal("80.00")

    # Price moves to 110 (no trail yet)
    exit_now, _, mod_sl = rm.on_tick(Decimal("110.00"))
    assert exit_now is False
    assert mod_sl is None
    assert rm.current_stop_loss == Decimal("80.00")

    # Price reaches 116 (activation threshold reached: +16 pts)
    # New SL = 80 + 15 = 95.00
    exit_now, _, mod_sl = rm.on_tick(Decimal("116.00"))
    assert exit_now is False
    assert mod_sl == Decimal("95.00")
    assert rm.current_stop_loss == Decimal("95.00")

    # Price steps up to 121 (+21 pts >= 15 + 5)
    # New SL = 95 + 5 = 100.00 (Breakeven locked!)
    exit_now, _, mod_sl = rm.on_tick(Decimal("121.00"))
    assert exit_now is False
    assert mod_sl == Decimal("100.00")
    assert rm.current_stop_loss == Decimal("100.00")

    # Price falls back to 110 -> SL must NOT move down
    exit_now, _, mod_sl = rm.on_tick(Decimal("110.00"))
    assert exit_now is False
    assert mod_sl is None
    assert rm.current_stop_loss == Decimal("100.00")

    # Price breaches trailing SL at 100 -> Triggers exit!
    exit_now, reason, _ = rm.on_tick(Decimal("99.50"))
    assert exit_now is True
    assert reason == "STOP_LOSS_HIT"

