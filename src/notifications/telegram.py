"""
src/notifications/telegram.py
Asynchronous Telegram bot notification service.
"""
from typing import Optional
import httpx
import logging

logger = logging.getLogger("TradeBot.Telegram")

class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.is_enabled = bool(bot_token and chat_id)

    async def send_message(self, text: str) -> bool:
        if not self.is_enabled:
            logger.info(f"[TELEGRAM SIMULATION]: {text}")
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to deliver Telegram notification: {e}")
            return False

