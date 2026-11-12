"""
src/data/feed_manager.py
Market data subscription manager with 3-second stale-feed watchdog.
"""
from typing import Dict, Callable, Any, Optional
from datetime import datetime
from decimal import Decimal
import asyncio
import logging
from src.core.clock import IClock

logger = logging.getLogger("TradeBot.FeedManager")

class StaleFeedException(Exception):
    pass

class MarketFeedManager:
    def __init__(self, clock: IClock, stale_timeout_seconds: float = 3.0):
        self.clock = clock
        self.stale_timeout = stale_timeout_seconds
        self.last_tick_time: Optional[datetime] = None
        self.latest_prices: Dict[str, Decimal] = {}
        self.tick_subscribers: Dict[str, list] = {}
        self._is_running = False

    def subscribe(self, symbol: str, callback: Callable[[Decimal], Any]) -> None:
        if symbol not in self.tick_subscribers:
            self.tick_subscribers[symbol] = []
        self.tick_subscribers[symbol].append(callback)

    def on_tick_received(self, symbol: str, price: Decimal) -> None:
        """Called whenever a tick arrives from the broker websocket."""
        self.last_tick_time = self.clock.now()
        self.latest_prices[symbol] = price
        
        # Dispatch to registered callbacks
        if symbol in self.tick_subscribers:
            for cb in self.tick_subscribers[symbol]:
                cb(price)

    def check_feed_health(self) -> bool:
        """Returns True if feed is active within stale_timeout; False otherwise."""
        if self.last_tick_time is None:
            return False
        delta = (self.clock.now() - self.last_tick_time).total_seconds()
        is_healthy = delta <= self.stale_timeout
        if not is_healthy:
            logger.warning(f"Feed STALE alert: Last tick was {delta:.2f}s ago (Timeout: {self.stale_timeout}s)")
        return is_healthy

