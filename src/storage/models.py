"""
src/storage/models.py
Relational Schema for Algorithmic Options Trading Bot.
Compatible with SQLite (WAL) and PostgreSQL.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Boolean, DateTime,
    ForeignKey, Text, Index, UniqueConstraint, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class TradingMode(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"

class BiasType(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class OptionType(str, Enum):
    CE = "CE"
    PE = "PE"

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    TRIGGERED = "TRIGGERED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    SQUARED_OFF = "SQUARED_OFF"

class SettingsVersion(Base):
    __tablename__ = "settings_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), default="user", nullable=False)
    
    reference_spot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reference_ce_avg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reference_pe_avg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    underlying: Mapped[str] = mapped_column(String(32), default="NIFTY", nullable=False)
    strike_selection_rule: Mapped[str] = mapped_column(String(32), default="ATM", nullable=False)
    expiry_preference: Mapped[str] = mapped_column(String(32), default="CURRENT_WEEK", nullable=False)
    lots: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    stop_loss_type: Mapped[str] = mapped_column(String(16), default="POINTS", nullable=False)
    stop_loss_value: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    target_type: Mapped[str] = mapped_column(String(16), default="POINTS", nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    trailing_sl_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trailing_sl_step: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0)
    
    mode: Mapped[str] = mapped_column(String(16), default="PAPER", nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), default="LIMIT_BUFFER", nullable=False)
    limit_buffer_points: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.50)
    max_slippage_points: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=2.00)
    max_bid_ask_spread: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=1.50)
    consecutive_ticks_confirm: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    max_daily_loss: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=5000.00, nullable=False)
    auto_square_off_time: Mapped[str] = mapped_column(String(8), default="15:15", nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text)

class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trading_date: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    settings_version_id: Mapped[int] = mapped_column(ForeignKey("settings_versions.id"), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    spot_symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    resolved_ce_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    resolved_pe_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    ce_instrument_token: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pe_instrument_token: Mapped[int] = mapped_column(BigInteger, nullable=False)
    lot_size: Mapped[int] = mapped_column(Integer, nullable=False)
    freeze_qty: Mapped[int] = mapped_column(Integer, nullable=False)

    settings_version: Mapped["SettingsVersion"] = relationship()

class MarketOpenPrice(Base):
    __tablename__ = "market_open_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trading_date: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    spot_open: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ce_open: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    pe_open: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    determined_bias: Mapped[str] = mapped_column(String(16), nullable=False)
    bias_rationale: Mapped[str] = mapped_column(Text, nullable=False)

class ConditionEvaluation(Base):
    __tablename__ = "condition_evaluations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    instrument_type: Mapped[str] = mapped_column(String(8), nullable=False)
    
    current_ltp: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cond1_open_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cond1_reference_val: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cond1_result: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    cond2_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cond2_user_avg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cond2_result: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    consecutive_confirmations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_fully_qualified: Mapped[bool] = mapped_column(Boolean, nullable=False)

class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    instrument: Mapped[str] = mapped_column(String(8), nullable=False)
    trading_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    side: Mapped[str] = mapped_column(String(8), default="BUY", nullable=False)
    trigger_ltp: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    is_winning_signal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    arbitration_note: Mapped[str] = mapped_column(String(255), nullable=False)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    broker_order_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    
    instrument_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    order_purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    limit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    trigger_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    status: Mapped[str] = mapped_column(String(24), default="SUBMITTED", nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    error_message: Mapped[Optional[str]] = mapped_column(Text)

class Fill(Base):
    __tablename__ = "fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    broker_fill_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    fill_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    filled_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    fill_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    brokerage_charges: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0)
    stt_and_taxes: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0)

    order: Mapped["Order"] = relationship()

class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trading_date: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    entry_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    current_stop_loss: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    target_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    highest_ltp_seen: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    exit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    exit_reason: Mapped[Optional[str]] = mapped_column(String(64))
    
    status: Mapped[str] = mapped_column(String(16), default="OPEN", nullable=False)
    gross_pnl: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0)
    net_pnl: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0)

class PnLDaily(Base):
    __tablename__ = "pnl_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trading_date: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    total_trades: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gross_pnl: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    total_charges: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0, nullable=False)
    net_pnl: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    max_drawdown_points: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0)

class EventLog(Base):
    __tablename__ = "events_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    event_name: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text)

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    channel: Mapped[str] = mapped_column(String(16), default="TELEGRAM", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class KillSwitchLog(Base):
    __tablename__ = "kill_switch_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    actions_taken: Mapped[str] = mapped_column(Text, nullable=False)

