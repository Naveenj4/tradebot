import React from 'react';
import { Check, X, Award } from 'lucide-react';
import type { EvaluatorState } from '../types';

interface ConditionMatrixProps {
  ce: EvaluatorState | undefined;
  pe: EvaluatorState | undefined;
}

export const ConditionMatrix: React.FC<ConditionMatrixProps> = ({ ce, pe }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      
      {/* CALL (CE) Evaluator */}
      <div className={`bg-[#0c111c] rounded-2xl p-5 relative overflow-hidden shadow-xl border transition-all ${
        ce?.is_triggered ? 'border-emerald-500/60 ring-1 ring-emerald-500/30' : 'border-emerald-950/40'
      }`}>
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <span className="w-3 h-3 rounded-full bg-emerald-400"></span>
            <h2 className="text-sm font-bold uppercase tracking-wider text-white">CALL Side (CE) Parallel Evaluator</h2>
          </div>
          <span className={`px-2.5 py-1 text-xs font-bold rounded mono flex items-center gap-1 ${
            ce?.is_triggered
              ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-300'
              : 'bg-slate-800 border border-slate-700 text-slate-400'
          }`}>
            {ce?.is_triggered ? <Award className="w-3.5 h-3.5" /> : null}
            {ce?.status_label ?? 'EVALUATING'}
          </span>
        </div>

        <div className="space-y-3.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Contract Symbol:</span>
            <span className="font-bold text-white mono text-sm">{ce?.symbol ?? 'NIFTY26NOV25400CE'}</span>
          </div>

          <div className="grid grid-cols-3 gap-2.5 text-center">
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">09:15 Open</div>
              <div className="text-sm font-bold text-slate-200 mono mt-0.5">{ce?.open?.toFixed(2) ?? '0.00'}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">User Average</div>
              <div className="text-sm font-bold text-slate-200 mono mt-0.5">{ce?.user_avg?.toFixed(2) ?? '0.00'}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Live LTP</div>
              <div className="text-sm font-extrabold text-emerald-400 mono mt-0.5">{ce?.ltp?.toFixed(2) ?? '0.00'}</div>
            </div>
          </div>

          <div className="space-y-2 pt-1 text-xs">
            <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">Condition 1: Option Open &gt; Reference</span>
              <span className={`font-bold mono flex items-center gap-1 ${ce?.cond1_open_gt_ref ? 'text-emerald-400' : 'text-slate-500'}`}>
                {ce?.cond1_open_gt_ref ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                {ce?.cond1_open_gt_ref ? `TRUE (${ce.open.toFixed(2)} > ${ce.reference_price.toFixed(2)})` : 'FALSE'}
              </span>
            </div>

            <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-300">Condition 2: Live LTP &gt; User Average</span>
              <span className={`font-bold mono flex items-center gap-1 ${ce?.cond2_ltp_gt_avg ? 'text-emerald-400' : 'text-slate-500'}`}>
                {ce?.cond2_ltp_gt_avg ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                {ce?.cond2_ltp_gt_avg ? `TRUE (${ce.ltp.toFixed(2)} > ${ce.user_avg.toFixed(2)})` : 'FALSE'}
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs">
            <span className="text-slate-400">Consecutive Tick Confirmations:</span>
            <div className="flex items-center gap-2">
              <div className="w-20 bg-slate-800 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-emerald-400 h-full transition-all duration-300" 
                  style={{ width: `${Math.min(100, ((ce?.consecutive_confirmations ?? 0) / (ce?.required_confirmations ?? 2)) * 100)}%` }}
                ></div>
              </div>
              <span className="font-extrabold text-emerald-300 mono">
                {ce?.consecutive_confirmations ?? 0} / {ce?.required_confirmations ?? 2}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* PUT (PE) Evaluator */}
      <div className={`bg-[#0c111c] rounded-2xl p-5 relative overflow-hidden shadow-xl border transition-all ${
        pe?.is_triggered ? 'border-rose-500/60 ring-1 ring-rose-500/30' : 'border-slate-800'
      }`}>
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <span className="w-3 h-3 rounded-full bg-slate-600"></span>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">PUT Side (PE) Parallel Evaluator</h2>
          </div>
          <span className={`px-2.5 py-1 text-xs font-bold rounded mono ${
            pe?.is_triggered
              ? 'bg-rose-500/20 border border-rose-500/30 text-rose-300'
              : 'bg-slate-800 border border-slate-700 text-slate-400'
          }`}>
            {pe?.status_label ?? 'SKIPPED'}
          </span>
        </div>

        <div className="space-y-3.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Contract Symbol:</span>
            <span className="font-bold text-slate-300 mono text-sm">{pe?.symbol ?? 'NIFTY26NOV25400PE'}</span>
          </div>

          <div className="grid grid-cols-3 gap-2.5 text-center">
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">09:15 Open</div>
              <div className="text-sm font-bold text-slate-400 mono mt-0.5">{pe?.open?.toFixed(2) ?? '0.00'}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">User Average</div>
              <div className="text-sm font-bold text-slate-400 mono mt-0.5">{pe?.user_avg?.toFixed(2) ?? '0.00'}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Live LTP</div>
              <div className="text-sm font-extrabold text-rose-400 mono mt-0.5">{pe?.ltp?.toFixed(2) ?? '0.00'}</div>
            </div>
          </div>

          <div className="space-y-2 pt-1 text-xs text-slate-400">
            <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
              <span>Condition 1: Option Open &gt; Reference</span>
              <span className={`font-semibold mono ${pe?.cond1_open_gt_ref ? 'text-emerald-400' : 'text-slate-500'}`}>
                {pe?.cond1_open_gt_ref ? 'TRUE' : 'N/A (Opposite skipped)'}
              </span>
            </div>

            <div className="flex justify-between items-center p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
              <span>Condition 2: Live LTP &gt; User Average</span>
              <span className={`font-semibold mono ${pe?.cond2_ltp_gt_avg ? 'text-emerald-400' : 'text-slate-500'}`}>
                {pe?.cond2_ltp_gt_avg ? 'TRUE' : 'N/A (Opposite skipped)'}
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Consecutive Tick Confirmations:</span>
            <div className="flex items-center gap-2">
              <div className="w-20 bg-slate-800 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-rose-400 h-full transition-all duration-300" 
                  style={{ width: `${Math.min(100, ((pe?.consecutive_confirmations ?? 0) / (pe?.required_confirmations ?? 2)) * 100)}%` }}
                ></div>
              </div>
              <span className="font-bold text-slate-500 mono">
                {pe?.consecutive_confirmations ?? 0} / {pe?.required_confirmations ?? 2}
              </span>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};
