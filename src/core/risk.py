"""
src/core/risk.py
Pre-trade safeguards and dynamic real-time exchange trailing SL manager.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple
from enum import Enum

class RiskRejectReason(str, Enum):
    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"
    DEPTH_TOO_THIN = "DEPTH_TOO_THIN"
    EXCEEDS_MAX_ORDER_VALUE = "EXCEEDS_MAX_ORDER_VALUE"
    EXCEEDS_MAX_LOTS = "EXCEEDS_MAX_LOTS"
    MAX_DAILY_LOSS_EXCEEDED = "MAX_DAILY_LOSS_EXCEEDED"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    OUTSIDE_TRIGGER_WINDOW = "OUTSIDE_TRIGGER_WINDOW"

@dataclass
class PreTradeRiskConfig:
    max_bid_ask_spread: Decimal = Decimal("2.0")
    min_market_depth: int = 100
    max_order_value: Decimal = Decimal("200000.0")
    max_lots: int = 10
    max_daily_loss: Decimal = Decimal("5000.0")

class DynamicPositionRiskManager:
    def __init__(
        self,
        entry_price: Decimal,
        quantity: int,
        stop_loss_points: Decimal,
        target_points: Decimal,
        trailing_enabled: bool = True,
        trailing_activation_points: Decimal = Decimal("15.0"),
        trailing_step_points: Decimal = Decimal("5.0")
    ):
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss_points = stop_loss_points
        self.target_points = target_points
        
        self.current_stop_loss = entry_price - stop_loss_points
        self.target_price = entry_price + target_points
        
        self.trailing_enabled = trailing_enabled
        self.trailing_activation_points = trailing_activation_points
        self.trailing_step_points = trailing_step_points
        
        self.highest_ltp_seen = entry_price
        self.is_trailing_active = False

    def on_tick(self, current_ltp: Decimal) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Dynamically handles price changes.
        Returns:
            (should_exit: bool, exit_reason: Optional[str], new_sl_to_modify: Optional[Decimal])
        """
        # 1. Target check
        if current_ltp >= self.target_price:
            return True, "TARGET_HIT", None

        # 2. Hard Stop Loss breach
        if current_ltp <= self.current_stop_loss:
            return True, "STOP_LOSS_HIT", None

        # 3. Dynamic Trailing SL Calculation
        new_sl_modification: Optional[Decimal] = None
        if self.trailing_enabled and current_ltp > self.highest_ltp_seen:
            self.highest_ltp_seen = current_ltp
            profit_points = self.highest_ltp_seen - self.entry_price
            
            if profit_points >= self.trailing_activation_points:
                self.is_trailing_active = True
                
                # Calculate new stepped trailing stop
                excess = profit_points - self.trailing_activation_points
                steps = int(excess // self.trailing_step_points)
                calculated_sl = (self.entry_price - self.stop_loss_points) + (self.trailing_activation_points + (steps * self.trailing_step_points))
                
                # SL must only ratchet upwards, never downwards
                if calculated_sl > self.current_stop_loss:
                    self.current_stop_loss = calculated_sl
                    new_sl_modification = self.current_stop_loss

        return False, None, new_sl_modification

