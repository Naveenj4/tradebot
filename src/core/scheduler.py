"""
src/core/scheduler.py
Trading schedule orchestrator for Asia/Kolkata session windows.
"""
from typing import Callable, Dict, Any
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger("TradeBot.Scheduler")
IST = pytz.timezone("Asia/Kolkata")

class TradingScheduler:
    def __init__(self):
        self._scheduler = AsyncIOScheduler(timezone=IST)
        self._jobs = {}

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Trading scheduler started.")

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Trading scheduler stopped.")

    def schedule_daily_task(self, task_id: str, time_str: str, callback: Callable[[], Any]) -> None:
        """
        Schedules a daily recurring task at 'HH:MM' IST on Monday-Friday.
        """
        hour, minute = map(int, time_str.split(":"))
        trigger = CronTrigger(
            day_of_week="mon-fri",
            hour=hour,
            minute=minute,
            second=0,
            timezone=IST
        )
        job = self._scheduler.add_job(
            callback,
            trigger=trigger,
            id=task_id,
            replace_existing=True
        )
        self._jobs[task_id] = job
        logger.info(f"Scheduled task [{task_id}] at {time_str} IST Mon-Fri")

