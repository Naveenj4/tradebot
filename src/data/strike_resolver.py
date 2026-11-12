"""
src/data/strike_resolver.py
Resolves ATM / ATM±N strikes from pre-open indicative price and finds nearest weekly expiry.
"""
from typing import List, Tuple, Optional
from decimal import Decimal
from datetime import datetime, date
import logging
from src.brokers.models import InstrumentInfo

logger = logging.getLogger("TradeBot.StrikeResolver")

class StrikeResolver:
    @staticmethod
    def calculate_atm_strike(index_level: Decimal, step: int = 50) -> int:
        """
        Rounds index level to nearest strike step (default 50 for Nifty).
        e.g., 25424 -> 25400, 25426 -> 25450.
        """
        val = float(index_level)
        rounded = round(val / step) * step
        return int(rounded)

    @staticmethod
    def resolve_contracts(
        instruments: List[InstrumentInfo],
        underlying: str,
        spot_price: Decimal,
        strike_rule: str = "ATM",
        today_date: Optional[date] = None
    ) -> Tuple[Optional[InstrumentInfo], Optional[InstrumentInfo]]:
        """
        Filters NFO instruments for the nearest weekly expiry and selects CE & PE.
        """
        if today_date is None:
            today_date = date.today()

        atm_strike = StrikeResolver.calculate_atm_strike(spot_price, step=50)
        
        # Determine target strike based on rule (ATM, ATM+1, ATM-1)
        target_strike = atm_strike
        if strike_rule == "ATM+1":
            target_strike = atm_strike + 50
        elif strike_rule == "ATM-1":
            target_strike = atm_strike - 50

        # Filter option contracts for the given underlying with expiry >= today
        candidates = [
            inst for inst in instruments
            if inst.name == underlying and inst.expiry is not None and inst.expiry.date() >= today_date
        ]

        if not candidates:
            logger.warning(f"No candidate option contracts found for {underlying}")
            return None, None

        # Find nearest expiry date
        nearest_expiry = min(inst.expiry for inst in candidates)

        ce_contract = None
        pe_contract = None

        for inst in candidates:
            if inst.expiry == nearest_expiry and inst.strike == Decimal(str(target_strike)):
                if inst.instrument_type == "CE":
                    ce_contract = inst
                elif inst.instrument_type == "PE":
                    pe_contract = inst

        logger.info(
            f"Resolved {underlying} Strike {target_strike} (Rule: {strike_rule}) | "
            f"Expiry: {nearest_expiry.strftime('%Y-%m-%d')} | "
            f"CE: {ce_contract.tradingsymbol if ce_contract else 'None'}, "
            f"PE: {pe_contract.tradingsymbol if pe_contract else 'None'}"
        )
        return ce_contract, pe_contract

