"""
src/core/race_arbiter.py
Thread-safe mutex preventing duplicate or competing entries.
Only the first valid qualified signal executes; the other side is immediately locked out.
Uses threading.Lock for sub-microsecond atomic serialization without socket dependencies.
"""
import threading
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from src.core.conditions import InstrumentSide

@dataclass(frozen=True)
class ExecutionSignal:
    instrument_side: InstrumentSide
    symbol: str
    trigger_price: Decimal
    timestamp: str
    reason: str

class RaceArbiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._winner: Optional[ExecutionSignal] = None
        self._is_sealed = False

    @property
    def has_winner(self) -> bool:
        return self._winner is not None

    @property
    def winner(self) -> Optional[ExecutionSignal]:
        return self._winner

    async def claim_execution(self, signal: ExecutionSignal) -> bool:
        """
        Attempts to claim the single daily execution token.
        Returns True if this signal acquired the token first; False otherwise.
        """
        return self.claim_sync(signal)

    def claim_sync(self, signal: ExecutionSignal) -> bool:
        """Synchronous atomic claim method."""
        if self._is_sealed:
            return False

        with self._lock:
            if self._winner is not None or self._is_sealed:
                return False
            
            self._winner = signal
            self._is_sealed = True
            return True

    def seal_window(self) -> None:
        """Explicitly seals the window (e.g. at 09:20:00 IST), forbidding further claims."""
        with self._lock:
            self._is_sealed = True

    def reset_for_new_day(self) -> None:
        """Resets the arbiter state for a fresh trading day."""
        with self._lock:
            self._winner = None
            self._is_sealed = False
