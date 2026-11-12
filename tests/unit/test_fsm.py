"""
tests/unit/test_fsm.py
Unit tests for BotLifecycleFSM state transitions.
"""
import pytest
from src.core.fsm import BotLifecycleFSM, BotState, InvalidStateTransition

def test_fsm_valid_lifecycle_transitions():
    fsm = BotLifecycleFSM(initial_state=BotState.SYSTEM_INIT)
    assert fsm.current_state == BotState.SYSTEM_INIT

    fsm.transition_to(BotState.RECONCILING, reason="Startup reconciliation")
    assert fsm.current_state == BotState.RECONCILING

    fsm.transition_to(BotState.WAITING_FOR_INPUT, reason="07:30 IST window")
    assert fsm.current_state == BotState.WAITING_FOR_INPUT

    fsm.transition_to(BotState.INPUT_LOCKED, reason="08:00 IST locked")
    assert fsm.current_state == BotState.INPUT_LOCKED

    fsm.transition_to(BotState.PREPARING_SESSION, reason="09:00 IST session prep")
    assert fsm.current_state == BotState.PREPARING_SESSION

def test_fsm_illegal_transition_raises():
    fsm = BotLifecycleFSM(initial_state=BotState.WAITING_FOR_INPUT)
    with pytest.raises(InvalidStateTransition):
        fsm.transition_to(BotState.POSITION_ACTIVE, reason="Illegal jump")

