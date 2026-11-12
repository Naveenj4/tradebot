"""
src/core/bias.py
Evaluates market direction at 09:15:00 IST using Spot Open vs Reference Spot.
"""
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

class BiasDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

@dataclass(frozen=True)
class BiasResult:
    direction: BiasDirection
    index_open: Decimal
    reference_spot: Decimal
    diff: Decimal
    rationale: str

class BiasEvaluator:
    @staticmethod
    def evaluate(index_open: Decimal, reference_spot: Decimal) -> BiasResult:
        diff = index_open - reference_spot
        if index_open > reference_spot:
            direction = BiasDirection.BULLISH
            rationale = f"Index Open ({index_open}) > Reference Spot ({reference_spot}) by +{diff} pts -> BULLISH (CALL Side)"
        elif index_open < reference_spot:
            direction = BiasDirection.BEARISH
            rationale = f"Index Open ({index_open}) < Reference Spot ({reference_spot}) by {diff} pts -> BEARISH (PUT Side)"
        else:
            direction = BiasDirection.NEUTRAL
            rationale = f"Index Open ({index_open}) == Reference Spot ({reference_spot}) -> NEUTRAL (No Trade Day)"

        return BiasResult(
            direction=direction,
            index_open=index_open,
            reference_spot=reference_spot,
            diff=diff,
            rationale=rationale
        )

