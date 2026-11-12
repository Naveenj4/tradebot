"""
src/core/clock.py
Time abstraction enabling identical execution in live production,
historical replay/backtesting, and unit tests.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import zoneinfo
import asyncio

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

class IClock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Returns the current aware datetime in IST."""
        pass

    @abstractmethod
    async def sleep(self, seconds: float) -> None:
        """Suspends execution for the specified duration."""
        pass

class RealClock(IClock):
    """Production clock tied to real-world system wall-clock."""
    def now(self) -> datetime:
        return datetime.now(IST)

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)

class SimulatedClock(IClock):
    """Deterministic simulated clock for tests and historical tick replay."""
    def __init__(self, start_time: datetime):
        if start_time.tzinfo is None:
            self._current_time = start_time.replace(tzinfo=IST)
        else:
            self._current_time = start_time.astimezone(IST)

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, new_time: datetime) -> None:
        if new_time.tzinfo is None:
            self._current_time = new_time.replace(tzinfo=IST)
        else:
            self._current_time = new_time.astimezone(IST)

    def advance(self, seconds: float) -> None:
        self._current_time += timedelta(seconds=seconds)

    async def sleep(self, seconds: float) -> None:
        self.advance(seconds)
        # Yield execution to allow co-routines to cycle
        await asyncio.sleep(0)

