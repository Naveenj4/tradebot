"""
tests/unit/test_window.py
Unit tests for trading session time boundaries using SimulatedClock.
"""
from datetime import datetime, time
import zoneinfo
from src.core.clock import SimulatedClock

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def test_window_boundaries():
    # 07:45 IST -> Inside pre-market input window (07:30 - 08:00)
    clock = SimulatedClock(datetime(2026, 11, 12, 7, 45, 0))
    t = clock.now().time()
    assert time(7, 30) <= t <= time(8, 0)

    # 08:05 IST -> Input locked
    clock.set_time(datetime(2026, 11, 12, 8, 5, 0))
    t = clock.now().time()
    assert not (time(7, 30) <= t <= time(8, 0))

    # 09:16 IST -> Inside trigger window (09:15 - 09:20)
    clock.set_time(datetime(2026, 11, 12, 9, 16, 30))
    t = clock.now().time()
    assert time(9, 15) <= t <= time(9, 20)

    # 09:20:01 IST -> Trigger window expired
    clock.set_time(datetime(2026, 11, 12, 9, 20, 1))
    t = clock.now().time()
    assert t > time(9, 20)

