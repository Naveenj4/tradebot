"""
config/settings.py
Global Configuration and Settings management using Pydantic v2 and PyYAML.
"""
from pathlib import Path
from typing import Optional, Literal
from decimal import Decimal
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class SystemConfig(BaseSettings):
    timezone: str = "Asia/Kolkata"
    data_directory: str = "./data"
    ticks_storage_directory: str = "./data/ticks"
    stale_feed_timeout_seconds: float = 3.0
    reconnect_backoff_base_seconds: float = 1.5
    max_reconnect_attempts: int = 10

class ScheduleConfig(BaseSettings):
    pre_market_input_start: str = "07:30"
    pre_market_input_lock: str = "08:00"
    broker_auth_time: str = "09:00"
    market_open_time: str = "09:15"
    trigger_window_end: str = "09:20"
    auto_square_off_time: str = "15:15"
    eod_backup_time: str = "15:45"

class StrategyConfig(BaseSettings):
    underlying: str = "NIFTY"
    strike_rule: str = "ATM"
    expiry_preference: str = "NEAREST_WEEKLY"
    expiry_roll_cutoff_time: str = "14:30"
    bias_reference_source: str = "USER_SPOT_VS_INDEX_OPEN"
    condition1_reference: str = "USER_AVERAGE"
    condition2_source: str = "LTP"
    consecutive_ticks_confirm: int = 2
    opposite_setup_action: str = "SKIP"
    direction_allowed: str = "BUY_ONLY"

class OrderExecutionConfig(BaseSettings):
    order_type: str = "LIMIT_BUFFER"
    limit_buffer_points: Decimal = Decimal("0.50")
    max_retries: int = 3
    retry_delay_ms: int = 250
    unfilled_0920_action: str = "CANCEL"

class RiskConfig(BaseSettings):
    max_trades_per_day: int = 1
    max_lots_cap: int = 10
    max_order_value_inr: Decimal = Decimal("200000.0")
    max_daily_loss_inr: Decimal = Decimal("5000.0")
    max_bid_ask_spread_points: Decimal = Decimal("2.0")
    min_market_depth_quantity: int = 100
    stop_loss_points: Decimal = Decimal("20.0")
    target_points: Decimal = Decimal("40.0")
    trailing_sl_enabled: bool = True
    trailing_activation_points: Decimal = Decimal("15.0")
    trailing_step_points: Decimal = Decimal("5.0")

class PaperEngineConfig(BaseSettings):
    fill_delay_ms: int = 50
    slippage_points: Decimal = Decimal("0.25")
    brokerage_per_order: Decimal = Decimal("20.0")
    stt_rate: Decimal = Decimal("0.000625")
    exchange_txn_fee_rate: Decimal = Decimal("0.000495")
    gst_rate: Decimal = Decimal("0.18")
    stamp_duty_rate: Decimal = Decimal("0.00003")

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Kolkata"
    DATABASE_URL: str = "sqlite+aiosqlite:///data/tradebot.db"

    TRADE_MODE: Literal["PAPER", "LIVE"] = "PAPER"
    CONFIRM_LIVE_TRADING_PHRASE: str = ""

    BROKER_TYPE: str = "ANGELONE"  # ANGELONE | KITE | PAPER

    # Angel One SmartAPI credentials
    ANGELONE_API_KEY: str = ""
    ANGELONE_CLIENT_ID: str = ""
    ANGELONE_PASSWORD: str = ""
    ANGELONE_TOTP_SECRET: str = ""

    # Zerodha Kite Connect credentials (alternative)
    KITE_API_KEY: str = ""
    KITE_API_SECRET: str = ""
    KITE_USER_ID: str = ""
    KITE_PASSWORD: str = ""
    KITE_TOTP_KEY: str = ""

    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    API_SECRET_KEY: str = "tradebot_default_secret_key"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"

    # Nested sub-configs
    system: SystemConfig = Field(default_factory=SystemConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    strategy: StrategyConfig = Field(default_factory=StrategyConfig)
    order_execution: OrderExecutionConfig = Field(default_factory=OrderExecutionConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    paper_engine: PaperEngineConfig = Field(default_factory=PaperEngineConfig)

    @classmethod
    def load_with_yaml(cls, yaml_path: Optional[Path] = None) -> "AppSettings":
        """Loads configuration merging YAML defaults with environment variables."""
        if yaml_path is None:
            yaml_path = BASE_DIR / "config" / "default_config.yaml"

        yaml_data = {}
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}

        settings = cls()

        # Merge YAML dictionaries into nested configs
        if "system" in yaml_data:
            settings.system = SystemConfig(**yaml_data["system"])
        if "schedule" in yaml_data:
            settings.schedule = ScheduleConfig(**yaml_data["schedule"])
        if "strategy" in yaml_data:
            settings.strategy = StrategyConfig(**yaml_data["strategy"])
        if "order_execution" in yaml_data:
            settings.order_execution = OrderExecutionConfig(**yaml_data["order_execution"])
        if "risk" in yaml_data:
            r = yaml_data["risk"]
            settings.risk = RiskConfig(
                max_trades_per_day=r.get("max_trades_per_day", 1),
                max_lots_cap=r.get("max_lots_cap", 10),
                max_order_value_inr=Decimal(str(r.get("max_order_value_inr", 200000.0))),
                max_daily_loss_inr=Decimal(str(r.get("max_daily_loss_inr", 5000.0))),
                max_bid_ask_spread_points=Decimal(str(r.get("max_bid_ask_spread_points", 2.0))),
                min_market_depth_quantity=r.get("min_market_depth_quantity", 100),
                stop_loss_points=Decimal(str(r.get("default_stop_loss", {}).get("value", 20.0))),
                target_points=Decimal(str(r.get("default_target", {}).get("value", 40.0))),
                trailing_sl_enabled=r.get("trailing_sl", {}).get("enabled", True),
                trailing_activation_points=Decimal(str(r.get("trailing_sl", {}).get("trail_after_points", 15.0))),
                trailing_step_points=Decimal(str(r.get("trailing_sl", {}).get("step_points", 5.0))),
            )
        if "paper_engine" in yaml_data:
            p = yaml_data["paper_engine"]
            c = p.get("charges", {})
            settings.paper_engine = PaperEngineConfig(
                fill_delay_ms=p.get("fill_delay_ms", 50),
                slippage_points=Decimal(str(p.get("slippage_points", 0.25))),
                brokerage_per_order=Decimal(str(c.get("brokerage_per_order", 20.0))),
                stt_rate=Decimal(str(c.get("stt_rate", 0.000625))),
                exchange_txn_fee_rate=Decimal(str(c.get("exchange_txn_fee_rate", 0.000495))),
                gst_rate=Decimal(str(c.get("gst_rate", 0.18))),
                stamp_duty_rate=Decimal(str(c.get("stamp_duty_rate", 0.00003))),
            )

        return settings

# Singleton global instance
global_settings = AppSettings.load_with_yaml()

