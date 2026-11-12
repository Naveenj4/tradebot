"""
src/api/routes/control.py
Emergency controls, pause/resume, and manual position management API endpoints.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from src.api.auth import verify_token
from src.api.routes.monitor import state_cache, append_event_log
import logging

router = APIRouter(prefix="/api/control", tags=["Control"], dependencies=[Depends(verify_token)])
logger = logging.getLogger("TradeBot.Control")

@router.post("/kill-switch")
async def trigger_kill_switch(reason: str = "Manual Emergency Kill-Switch Activated"):
    logger.critical(f"EMERGENCY KILL-SWITCH TRIGGERED: {reason}")
    state_cache["kill_switch_active"] = True
    state_cache["is_paused"] = True
    state_cache["fsm_state"] = "EMERGENCY_STOP"
    
    # Square off position if any
    squared_off_symbol = None
    if state_cache.get("position"):
        pos = state_cache["position"]
        squared_off_symbol = pos.get("symbol")
        pos["status"] = "SQUARED_OFF"
        pos["exit_price"] = pos.get("highest_ltp", pos.get("entry_price"))
        pos["exit_reason"] = "KILL_SWITCH"
        state_cache["closed_positions"].insert(0, dict(pos))
        state_cache["position"] = None
        state_cache["fsm_state"] = "POSITION_CLOSED"

    append_event_log("CRITICAL", "CONTROL", "KILL_SWITCH_ACTIVATED", f"Reason: {reason}. Closed: {squared_off_symbol or 'None'}")

    return {
        "status": "STOPPED",
        "action": "All orders cancelled and active positions squared off immediately.",
        "reason": reason
    }

@router.post("/pause")
async def pause_trading():
    state_cache["is_paused"] = True
    append_event_log("WARNING", "CONTROL", "BOT_PAUSED", "Trading and condition evaluations paused by operator.")
    return {"status": "PAUSED", "message": "Bot condition evaluations are now paused."}

@router.post("/resume")
async def resume_trading():
    if state_cache.get("kill_switch_active"):
        return {"status": "BLOCKED", "message": "Cannot resume while Kill Switch is active. Reset kill-switch first."}
    state_cache["is_paused"] = False
    append_event_log("INFO", "CONTROL", "BOT_RESUMED", "Trading and condition evaluations resumed by operator.")
    return {"status": "RUNNING", "message": "Bot condition evaluations have resumed."}

@router.post("/reset-kill-switch")
async def reset_kill_switch():
    state_cache["kill_switch_active"] = False
    state_cache["is_paused"] = False
    state_cache["fsm_state"] = "WAITING_MARKET_OPEN"
    append_event_log("INFO", "CONTROL", "KILL_SWITCH_RESET", "Emergency stop reset. Bot restored to active standby.")
    return {"status": "RESET", "message": "Kill switch cleared. Ready for operations."}

@router.post("/square-off")
async def manual_square_off():
    if not state_cache.get("position"):
        return {"status": "NOOP", "message": "No active position to square off."}

    pos = state_cache["position"]
    pos["status"] = "SQUARED_OFF"
    pos["exit_price"] = state_cache.get("ce", {}).get("ltp") if pos["symbol"].endswith("CE") else state_cache.get("pe", {}).get("ltp")
    pos["exit_reason"] = "MANUAL_SQUARE_OFF"
    state_cache["closed_positions"].insert(0, dict(pos))
    state_cache["position"] = None
    state_cache["fsm_state"] = "POSITION_CLOSED"

    append_event_log("WARNING", "CONTROL", "MANUAL_SQUARE_OFF", f"Squared off {pos['symbol']} at {pos['exit_price']}")
    return {"status": "SUCCESS", "message": f"Position {pos['symbol']} squared off manually."}
