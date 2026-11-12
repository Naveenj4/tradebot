"""
src/api/routes/orders.py
Orders ledger, execution fills, and positions history API endpoints.
"""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from src.api.auth import verify_token
from src.api.routes.monitor import state_cache

router = APIRouter(prefix="/api/orders", tags=["Orders"], dependencies=[Depends(verify_token)])

orders_data: List[Dict[str, Any]] = [
    {
        "order_id": "ANGEL_ORD_9823101",
        "date": "2026-11-12",
        "time": "09:16:04",
        "symbol": "NIFTY26NOV25400CE",
        "side": "BUY",
        "type": "LIMIT",
        "qty": 50,
        "price": 123.00,
        "trigger_price": None,
        "status": "FILLED",
        "purpose": "ENTRY"
    },
    {
        "order_id": "ANGEL_SL_9823102",
        "date": "2026-11-12",
        "time": "09:16:05",
        "symbol": "NIFTY26NOV25400CE",
        "side": "SELL",
        "type": "STOPLOSS_LIMIT",
        "qty": 50,
        "price": 101.50,
        "trigger_price": 102.50,
        "status": "TRIGGER_PENDING",
        "purpose": "STOP_LOSS"
    },
    {
        "order_id": "ANGEL_ORD_8711091",
        "date": "2026-11-11",
        "time": "09:16:10",
        "symbol": "NIFTY26NOV25350PE",
        "side": "BUY",
        "type": "LIMIT",
        "qty": 50,
        "price": 85.50,
        "trigger_price": None,
        "status": "FILLED",
        "purpose": "ENTRY"
    },
    {
        "order_id": "ANGEL_ORD_8711092",
        "date": "2026-11-11",
        "time": "10:45:22",
        "symbol": "NIFTY26NOV25350PE",
        "side": "SELL",
        "type": "LIMIT",
        "qty": 50,
        "price": 115.00,
        "trigger_price": None,
        "status": "FILLED",
        "purpose": "TARGET"
    }
]

@router.get("/list")
async def get_orders():
    return orders_data

@router.get("/positions")
async def get_all_positions():
    active = [state_cache["position"]] if state_cache.get("position") else []
    closed = state_cache.get("closed_positions", [])
    return {
        "active": active,
        "closed": closed
    }

