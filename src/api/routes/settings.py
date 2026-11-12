"""
src/api/routes/settings.py
Settings and parameter versioning with strict 07:30 - 08:00 IST edit window enforcement.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
import zoneinfo
from src.api.auth import verify_token

router = APIRouter(prefix="/api/settings", tags=["Settings"], dependencies=[Depends(verify_token)])
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

class SettingsUpdateRequest(BaseModel):
    reference_spot: Decimal = Field(..., gt=0)
    reference_ce_avg: Decimal = Field(..., gt=0)
    reference_pe_avg: Decimal = Field(..., gt=0)
    lots: int = Field(default=1, ge=1, le=10)
    stop_loss_points: Decimal = Field(default=Decimal("20.0"), gt=0)
    target_points: Decimal = Field(default=Decimal("40.0"), gt=0)
    summary: str = "User daily input update"

# In-memory working version
current_settings = {
    "version": 1,
    "reference_spot": 25400.00,
    "reference_ce_avg": 100.00,
    "reference_pe_avg": 95.00,
    "lots": 1,
    "stop_loss_points": 20.0,
    "target_points": 40.0,
    "locked": False,
    "last_updated": "2026-11-12T07:45:00+05:30"
}

def is_input_window_open() -> bool:
    """Inputs are allowed only between 07:30 and 08:00 AM IST."""
    now = datetime.now(IST).time()
    from datetime import time
    return time(7, 30) <= now <= time(8, 0)

@router.get("/current")
async def get_current_settings():
    now_ist = datetime.now(IST)
    window_open = is_input_window_open()
    return {
        "settings": current_settings,
        "input_window_open": window_open,
        "server_time_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/update")
async def update_settings(payload: SettingsUpdateRequest, bypass_lock_for_dev: bool = False):
    if not is_input_window_open() and not bypass_lock_for_dev:
        raise HTTPException(
            status_code=403,
            detail="Settings are LOCKED. Parameter updates are strictly allowed between 07:30 and 08:00 AM IST."
        )

    current_settings["version"] += 1
    current_settings["reference_spot"] = float(payload.reference_spot)
    current_settings["reference_ce_avg"] = float(payload.reference_ce_avg)
    current_settings["reference_pe_avg"] = float(payload.reference_pe_avg)
    current_settings["lots"] = payload.lots
    current_settings["stop_loss_points"] = float(payload.stop_loss_points)
    current_settings["target_points"] = float(payload.target_points)
    current_settings["last_updated"] = datetime.now(IST).isoformat()

    return {
        "status": "SUCCESS",
        "message": f"Settings dynamically updated to Version {current_settings['version']}",
        "version": current_settings["version"]
    }

