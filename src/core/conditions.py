"""
src/core/conditions.py
High-frequency dynamic condition evaluation running on incoming ticks.
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
from src.core.bias import BiasDirection

class InstrumentSide(str, Enum):
    CE = "CE"
    PE = "PE"

class OppositeAction(str, Enum):
    SKIP = "SKIP"
    BUY_OPPOSITE = "BUY_OPPOSITE"
    SELL = "SELL"

@dataclass
class ConditionState:
    instrument_side: InstrumentSide
    open_price: Decimal
    current_ltp: Decimal
    user_average: Decimal
    reference_price: Decimal
    
    cond1_passed: bool = False
    cond2_passed: bool = False
    consecutive_confirmations: int = 0
    is_triggered: bool = False
    reason: str = ""

class ConditionEngine:
    def __init__(
        self,
        instrument_side: InstrumentSide,
        user_average: Decimal,
        opposite_action: OppositeAction = OppositeAction.SKIP,
        required_confirmations: int = 2
    ):
        self.instrument_side = instrument_side
        self.user_average = user_average
        self.reference_price = user_average  # Configurable: user_average as decided in Sec 11
        self.opposite_action = opposite_action
        self.required_confirmations = required_confirmations
        
        self.open_price: Optional[Decimal] = None
        self._consecutive_count = 0

    def set_open_price(self, open_price: Decimal) -> None:
        self.open_price = open_price

    def evaluate_tick(self, ltp: Decimal, bias: BiasDirection) -> ConditionState:
        """
        Dynamically evaluated on every market tick.
        """
        if self.open_price is None:
            return ConditionState(
                instrument_side=self.instrument_side,
                open_price=Decimal("0.0"),
                current_ltp=ltp,
                user_average=self.user_average,
                reference_price=self.reference_price,
                reason="Waiting for instrument 09:15 open price"
            )

        # Check alignment with Market Bias
        is_aligned = (
            (bias == BiasDirection.BULLISH and self.instrument_side == InstrumentSide.CE) or
            (bias == BiasDirection.BEARISH and self.instrument_side == InstrumentSide.PE)
        )

        cond1_passed = False
        cond2_passed = False

        if is_aligned:
            # Primary Setup:
            # Condition 1: Option Open > Reference (User Average)
            # Condition 2: Option LTP > User Average
            cond1_passed = self.open_price > self.reference_price
            cond2_passed = ltp > self.user_average
        else:
            # Opposite Setup (PE in Bullish / CE in Bearish)
            if self.opposite_action == OppositeAction.SKIP:
                self._consecutive_count = 0
                return ConditionState(
                    instrument_side=self.instrument_side,
                    open_price=self.open_price,
                    current_ltp=ltp,
                    user_average=self.user_average,
                    reference_price=self.reference_price,
                    cond1_passed=False,
                    cond2_passed=False,
                    consecutive_confirmations=0,
                    is_triggered=False,
                    reason=f"Opposite setup detected ({self.instrument_side.value} during {bias.value}); configured to SKIP"
                )
            else:
                cond1_passed = self.open_price < self.reference_price
                cond2_passed = ltp < self.user_average

        # Check if both conditions hold simultaneously
        if cond1_passed and cond2_passed:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 0

        is_triggered = self._consecutive_count >= self.required_confirmations

        reason = (
            f"Qualified ({self._consecutive_count}/{self.required_confirmations} ticks)"
            if is_triggered
            else f"C1(Open>{self.reference_price})={cond1_passed}, C2(LTP>{self.user_average})={cond2_passed}"
        )

        return ConditionState(
            instrument_side=self.instrument_side,
            open_price=self.open_price,
            current_ltp=ltp,
            user_average=self.user_average,
            reference_price=self.reference_price,
            cond1_passed=cond1_passed,
            cond2_passed=cond2_passed,
            consecutive_confirmations=self._consecutive_count,
            is_triggered=is_triggered,
            reason=reason
        )

