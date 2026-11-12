import React from 'react';
import { Activity, TrendingUp, TrendingDown, Briefcase, Target } from 'lucide-react';
import type { TelemetryState } from '../types';

interface MetricCardsProps {
  state: TelemetryState | null;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ state }) => {
  const spotPrice = state?.spot_price ?? 25420.50;
  const refSpot = state?.user_reference_spot ?? 25400.00;
  const bias = state?.bias ?? 'BULLISH';
  const biasRationale = state?.bias_rationale ?? 'Open > Ref Spot';

  const position = state?.position;
  const pnl = position?.unrealized_pnl ?? 0;
  const isPnlPositive = pnl >= 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      {/* Spot Index Card */}
      <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">NIFTY 50 Spot</div>
          <div className="text-2xl font-black text-amber-400 mono mt-1">
            {spotPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            User Ref: <span className="text-slate-300 font-semibold mono">{refSpot.toFixed(2)}</span>
          </div>
        </div>
        <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
          <Activity className="w-5 h-5 text-amber-400" />
        </div>
      </div>

      {/* Market Bias Card */}
      <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Market Bias (09:15)</div>
          <div className={`text-2xl font-black mono mt-1 flex items-center gap-1.5 ${
            bias === 'BULLISH' ? 'text-emerald-400' : bias === 'BEARISH' ? 'text-rose-400' : 'text-slate-300'
          }`}>
            <span>{bias} ({bias === 'BULLISH' ? 'CE' : bias === 'BEARISH' ? 'PE' : 'NONE'})</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1 truncate max-w-[220px]" title={biasRationale}>
            {biasRationale}
          </div>
        </div>
        <div className={`w-10 h-10 rounded-lg border flex items-center justify-center ${
          bias === 'BULLISH' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20'
        }`}>
          {bias === 'BULLISH' ? <TrendingUp className="w-5 h-5 text-emerald-400" /> : <TrendingDown className="w-5 h-5 text-rose-400" />}
        </div>
      </div>

      {/* Active Position Card */}
      <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Active Position</div>
          <div className="text-base font-extrabold text-white mono mt-1 truncate max-w-[190px]">
            {position ? `${position.symbol} (${position.quantity} Q)` : 'NO ACTIVE POSITION'}
          </div>
          <div className={`text-[11px] font-extrabold mono mt-1 ${position ? (isPnlPositive ? 'text-emerald-400' : 'text-rose-400') : 'text-slate-500'}`}>
            PnL: {position ? `${isPnlPositive ? '+' : ''}₹${pnl.toFixed(2)}` : '₹0.00'}
          </div>
        </div>
        <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
          <Briefcase className="w-5 h-5 text-blue-400" />
        </div>
      </div>

      {/* Trailing SL & Target Card */}
      <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Dynamic Trailing SL</div>
          <div className="text-2xl font-black text-rose-400 mono mt-1">
            {position ? position.current_sl.toFixed(2) : '--'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Target: <span className="text-slate-300 font-semibold mono">{position ? position.target.toFixed(2) : '--'}</span>
          </div>
        </div>
        <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center">
          <Target className="w-5 h-5 text-rose-400" />
        </div>
      </div>

    </div>
  );
};
