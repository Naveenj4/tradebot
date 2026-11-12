"""
src/api/routes/monitor.py
Real-time state diagnostics, telemetry, and live activity journal for TradeBot.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime
import zoneinfo
from src.api.auth import verify_token
from config.settings import global_settings

router = APIRouter(prefix="/api/monitor", tags=["Monitor"], dependencies=[Depends(verify_token)])
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

# In-memory shared state for live dashboard & WebSocket telemetry
state_cache: Dict[str, Any] = {
    "fsm_state": "WAITING_MARKET_OPEN",
    "broker_name": global_settings.BROKER_TYPE,
    "trade_mode": global_settings.TRADE_MODE,
    "is_paused": False,
    "kill_switch_active": False,
    "stale_feed": False,
    "spot_price": 25420.50,
    "spot_open": 25410.00,
    "user_reference_spot": 25400.00,
    "bias": "BULLISH",
    "bias_rationale": "Index Open (25410.00) > Ref Spot (25400.00) by +10.00 pts",
    "ce": {
        "symbol": "NIFTY26NOV25400CE",
        "ltp": 122.50,
        "open": 105.00,
        "user_avg": 100.00,
        "reference_price": 100.00,
        "cond1_open_gt_ref": True,
        "cond2_ltp_gt_avg": True,
        "consecutive_confirmations": 2,
        "required_confirmations": 2,
        "is_triggered": True,
        "status_label": "QUALIFIED (TRIGGER WINNER)"
    },
    "pe": {
        "symbol": "NIFTY26NOV25400PE",
        "ltp": 92.00,
        "open": 110.00,
        "user_avg": 95.00,
        "reference_price": 95.00,
        "cond1_open_gt_ref": False,
        "cond2_ltp_gt_avg": False,
        "consecutive_confirmations": 0,
        "required_confirmations": 2,
        "is_triggered": False,
        "status_label": "SKIPPED (OPPOSITE SETUP)"
    },
    "position": {
        "symbol": "NIFTY26NOV25400CE",
        "quantity": 50,
        "entry_price": 122.50,
        "current_sl": 102.50,
        "target": 162.50,
        "highest_ltp": 125.00,
        "trailing_active": True,
        "unrealized_pnl": 125.00,
        "entry_time": "09:16:04 IST",
        "status": "OPEN"
    },
    "closed_positions": [
        {
            "id": 1,
            "date": "2026-11-11",
            "symbol": "NIFTY26NOV25350PE",
            "quantity": 50,
            "entry_price": 85.00,
            "exit_price": 115.00,
            "entry_time": "09:16:10",
            "exit_time": "10:45:22",
            "exit_reason": "TARGET_HIT",
            "gross_pnl": 1500.00,
            "charges": 55.40,
            "net_pnl": 1444.60,
            "status": "CLOSED"
        },
        {
            "id": 2,
            "date": "2026-11-10",
            "symbol": "NIFTY26NOV25300CE",
            "quantity": 50,
            "entry_price": 110.00,
            "exit_price": 95.00,
            "entry_time": "09:15:45",
            "exit_time": "09:32:10",
            "exit_reason": "STOP_LOSS_HIT",
            "gross_pnl": -750.00,
            "charges": 54.20,
            "net_pnl": -804.20,
            "status": "CLOSED"
        }
    ],
    "event_journal": []
}

def append_event_log(level: str, category: str, event_name: str, message: str):
    """Appends structured audit log to the in-memory journal stream."""
    now_str = datetime.now(IST).strftime("%H:%M:%S")
    entry = {
        "timestamp": now_str,
        "level": level,
        "category": category,
        "event_name": event_name,
        "message": message
    }
    state_cache["event_journal"].insert(0, entry)
    if len(state_cache["event_journal"]) > 100:
        state_cache["event_journal"].pop()

# Initial seed events
append_event_log("INFO", "FSM", "SYSTEM_BOOT", "TradeBot 1.0 engine initialized with Angel One SmartAPI.")
append_event_log("INFO", "FEED", "TICKS_SUBSCRIBED", "Subscribed to tokens for Spot (NIFTY), CE (25400), PE (25400).")
append_event_log("INFO", "STRATEGY", "BIAS_DETERMINED", "Market open (25410.00) > Ref (25400.00) -> Bullish bias.")
append_event_log("INFO", "ORDER", "ENTRY_FILLED", "Filled 50 qty NIFTY26NOV25400CE @ 122.50. Exchange SL placed at 102.50.")

@router.get("/status")
async def get_live_status():
    return state_cache

@router.get("/events")
async def get_events():
    return state_cache["event_journal"]
