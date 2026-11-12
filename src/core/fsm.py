"""
src/core/fsm.py
State Machine strictly governing transitions throughout the trading day.
"""
from enum import Enum
from typing import Callable, Dict, List, Optional
import logging

logger = logging.getLogger("TradeBot.FSM")

class BotState(str, Enum):
    SYSTEM_INIT = "SYSTEM_INIT"
    RECONCILING = "RECONCILING"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"      # 07:30 - 08:00
    INPUT_LOCKED = "INPUT_LOCKED"                # 08:00 - 09:00
    PREPARING_SESSION = "PREPARING_SESSION"      # 09:00 - 09:08
    CONNECTING_FEED = "CONNECTING_FEED"          # 09:08 - 09:14:59
    WAITING_MARKET_OPEN = "WAITING_MARKET_OPEN"  # 09:14:59
    CAPTURING_OPEN = "CAPTURING_OPEN"            # 09:15:00
    EVALUATING_TRIGGERS = "EVALUATING_TRIGGERS"  # 09:15:00 - 09:20:00
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    POSITION_ACTIVE = "POSITION_ACTIVE"
    POSITION_CLOSED = "POSITION_CLOSED"
    AUTO_SQUAREOFF = "AUTO_SQUAREOFF"
    MONITORING_EOD = "MONITORING_EOD"
    ARCHIVING_AND_BACKUP = "ARCHIVING_AND_BACKUP"
    SYSTEM_IDLE = "SYSTEM_IDLE"
    EMERGENCY_STOP = "EMERGENCY_STOP"

class InvalidStateTransition(Exception):
    pass

class BotLifecycleFSM:
    VALID_TRANSITIONS: Dict[BotState, List[BotState]] = {
        BotState.SYSTEM_INIT: [BotState.RECONCILING, BotState.EMERGENCY_STOP],
        BotState.RECONCILING: [BotState.WAITING_FOR_INPUT, BotState.EMERGENCY_STOP],
        BotState.WAITING_FOR_INPUT: [BotState.INPUT_LOCKED, BotState.EMERGENCY_STOP],
        BotState.INPUT_LOCKED: [BotState.PREPARING_SESSION, BotState.EMERGENCY_STOP],
        BotState.PREPARING_SESSION: [BotState.CONNECTING_FEED, BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.CONNECTING_FEED: [BotState.WAITING_MARKET_OPEN, BotState.EMERGENCY_STOP],
        BotState.WAITING_MARKET_OPEN: [BotState.CAPTURING_OPEN, BotState.EMERGENCY_STOP],
        BotState.CAPTURING_OPEN: [BotState.EVALUATING_TRIGGERS, BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.EVALUATING_TRIGGERS: [BotState.ORDER_SUBMITTED, BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.ORDER_SUBMITTED: [BotState.POSITION_ACTIVE, BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.POSITION_ACTIVE: [BotState.POSITION_CLOSED, BotState.AUTO_SQUAREOFF, BotState.EMERGENCY_STOP],
        BotState.POSITION_CLOSED: [BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.AUTO_SQUAREOFF: [BotState.MONITORING_EOD, BotState.EMERGENCY_STOP],
        BotState.MONITORING_EOD: [BotState.ARCHIVING_AND_BACKUP, BotState.EMERGENCY_STOP],
        BotState.ARCHIVING_AND_BACKUP: [BotState.SYSTEM_IDLE, BotState.EMERGENCY_STOP],
        BotState.SYSTEM_IDLE: [BotState.WAITING_FOR_INPUT, BotState.EMERGENCY_STOP],
        BotState.EMERGENCY_STOP: [BotState.MONITORING_EOD]
    }

    def __init__(self, initial_state: BotState = BotState.SYSTEM_INIT):
        self._state = initial_state
        self._listeners: List[Callable[[BotState, BotState, str], None]] = []

    @property
    def current_state(self) -> BotState:
        return self._state

    def add_transition_listener(self, listener: Callable[[BotState, BotState, str], None]) -> None:
        self._listeners.append(listener)

    def transition_to(self, new_state: BotState, reason: str = "") -> None:
        if new_state not in self.VALID_TRANSITIONS.get(self._state, []):
            raise InvalidStateTransition(
                f"Illegal transition requested: {self._state.value} -> {new_state.value}. (Reason: {reason})"
            )
        old_state = self._state
        self._state = new_state
        logger.info(f"FSM State changed: [{old_state.value}] -> [{new_state.value}] | Reason: {reason}")
        for listener in self._listeners:
            listener(old_state, new_state, reason)

