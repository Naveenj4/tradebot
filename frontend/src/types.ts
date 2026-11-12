export interface EvaluatorState {
  symbol: string;
  ltp: number;
  open: number;
  user_avg: number;
  reference_price: number;
  cond1_open_gt_ref: boolean;
  cond2_ltp_gt_avg: boolean;
  consecutive_confirmations: number;
  required_confirmations: number;
  is_triggered: boolean;
  status_label: string;
}

export interface ActivePosition {
  symbol: string;
  quantity: number;
  entry_price: number;
  current_sl: number;
  target: number;
  highest_ltp: number;
  trailing_active: boolean;
  unrealized_pnl: number;
  entry_time: string;
  status: string;
}

export interface ClosedPosition {
  id: number;
  date: string;
  symbol: string;
  quantity: number;
  entry_price: number;
  exit_price: number;
  entry_time: string;
  exit_time: string;
  exit_reason: string;
  gross_pnl: number;
  charges: number;
  net_pnl: number;
  status: string;
}

export interface EventLog {
  timestamp: string;
  level: string;
  category: string;
  event_name: string;
  message: string;
}

export interface TelemetryState {
  fsm_state: string;
  broker_name: string;
  trade_mode: string;
  is_paused: boolean;
  kill_switch_active: boolean;
  stale_feed: boolean;
  spot_price: number;
  spot_open: number;
  user_reference_spot: number;
  bias: string;
  bias_rationale: string;
  ce: EvaluatorState;
  pe: EvaluatorState;
  position: ActivePosition | null;
  closed_positions: ClosedPosition[];
  event_journal: EventLog[];
}

export interface OrderItem {
  order_id: string;
  date: string;
  time: string;
  symbol: string;
  side: string;
  type: string;
  qty: number;
  price: number | null;
  trigger_price: number | null;
  status: string;
  purpose: string;
}

export interface PerformanceReport {
  metrics: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate_pct: number;
    profit_factor: number;
    gross_pnl: number;
    total_charges: number;
    net_pnl: number;
    max_drawdown: number;
  };
  breakdown: {
    ce_count: number;
    ce_pnl: number;
    pe_count: number;
    pe_pnl: number;
  };
  equity_curve: {
    date: string;
    pnl: number;
    cumulative: number;
  }[];
}

