"""
src/main.py
Root entrypoint for TradeBot 1.0.
Initializes Database, Clock, Broker Adapter, FSM, and Scheduler.
Supports brokers: ANGELONE (default), KITE, PAPER.
"""
import asyncio
import logging
from decimal import Decimal
from datetime import datetime
import uvicorn

from config.settings import global_settings
from src.core.clock import RealClock
from src.core.fsm import BotLifecycleFSM, BotState
from src.core.bias import BiasEvaluator, BiasDirection
from src.core.conditions import ConditionEngine, InstrumentSide, OppositeAction
from src.core.race_arbiter import RaceArbiter, ExecutionSignal
from src.core.risk import DynamicPositionRiskManager, PreTradeRiskConfig
from src.brokers.mock.paper_broker import PaperBrokerAdapter
from src.execution.order_manager import OrderExecutionManager
from src.execution.reconciler import StartupReconciler
from src.data.feed_manager import MarketFeedManager
from src.storage.session import init_db, AsyncSessionLocal
from src.storage.repository import SettingsRepository
from src.notifications.telegram import TelegramNotifier
from src.api.app import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("TradeBot.Main")


def create_broker_adapter(settings):
    """
    Factory method to instantiate the correct broker adapter based on BROKER_TYPE.
    Supports: ANGELONE, KITE, PAPER (or any TRADE_MODE=PAPER override).
    """
    broker_type = settings.BROKER_TYPE.upper()
    trade_mode = settings.TRADE_MODE.upper()

    # Paper mode always uses the mock engine regardless of BROKER_TYPE
    if trade_mode == "PAPER":
        logger.info("Initializing in PAPER TRADING MODE (simulated matching engine).")
        return PaperBrokerAdapter(settings.paper_engine)

    # --- LIVE mode ---
    if broker_type == "ANGELONE":
        from src.brokers.angelone.adapter import AngelOneBrokerAdapter
        logger.warning("Initializing in LIVE TRADING MODE -> Angel One SmartAPI.")
        return AngelOneBrokerAdapter(
            api_key=settings.ANGELONE_API_KEY,
            client_id=settings.ANGELONE_CLIENT_ID,
            password=settings.ANGELONE_PASSWORD,
            totp_secret=settings.ANGELONE_TOTP_SECRET,
        )

    elif broker_type == "KITE":
        from src.brokers.kite.adapter import KiteBrokerAdapter
        logger.warning("Initializing in LIVE TRADING MODE -> Zerodha Kite Connect.")
        return KiteBrokerAdapter(
            api_key=settings.KITE_API_KEY,
            api_secret=settings.KITE_API_SECRET,
            user_id=settings.KITE_USER_ID,
            password=settings.KITE_PASSWORD,
            totp_key=settings.KITE_TOTP_KEY,
        )

    else:
        logger.error(f"Unknown BROKER_TYPE: {broker_type}. Falling back to PAPER mode.")
        return PaperBrokerAdapter(settings.paper_engine)


class TradingBotOrchestrator:
    def __init__(self):
        self.settings = global_settings
        self.clock = RealClock()
        self.fsm = BotLifecycleFSM()
        self.feed_manager = MarketFeedManager(self.clock, stale_timeout_seconds=3.0)
        self.race_arbiter = RaceArbiter()
        self.telegram = TelegramNotifier(
            bot_token=self.settings.TELEGRAM_BOT_TOKEN,
            chat_id=self.settings.TELEGRAM_CHAT_ID
        )

        # Select broker adapter via factory
        self.broker = create_broker_adapter(self.settings)

        self.order_manager = OrderExecutionManager(self.broker)
        self.reconciler = StartupReconciler(self.broker)
        self.risk_manager: DynamicPositionRiskManager = None

    async def initialize(self):
        logger.info("Initializing TradeBot 1.0 storage and database tables...")
        await init_db()

        # Startup reconciliation
        self.fsm.transition_to(BotState.RECONCILING, reason="Reconciling startup state")
        today_str = self.clock.now().strftime("%Y-%m-%d")
        async with AsyncSessionLocal() as session:
            rec = await self.reconciler.reconcile(session, today_str)
            logger.info(f"Reconciliation completed: {rec}")

        self.fsm.transition_to(BotState.WAITING_FOR_INPUT, reason="Ready for daily parameters")


async def run_server():
    bot = TradingBotOrchestrator()
    await bot.initialize()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run_server())
