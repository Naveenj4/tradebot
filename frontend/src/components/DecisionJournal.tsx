import React from 'react';
import { Radio } from 'lucide-react';
import type { EventLog } from '../types';

interface DecisionJournalProps {
  logs: EventLog[] | undefined;
}

export const DecisionJournal: React.FC<DecisionJournalProps> = ({ logs }) => {
  const getBadgeColor = (lvl: string) => {
    if (lvl === 'CRITICAL') return 'bg-rose-500/20 text-rose-300 border border-rose-500/30';
    if (lvl === 'WARNING') return 'bg-amber-500/20 text-amber-300 border border-amber-500/30';
    return 'bg-blue-500/20 text-blue-300 border border-blue-500/30';
  };

  return (
    <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-emerald-400 animate-pulse-subtle" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Live Decision & Activity Journal</h3>
        </div>
        <span className="text-[11px] text-slate-500">Auto-streaming sub-millisecond bot evaluations</span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto custom-scrollbar font-mono text-xs">
        {logs && logs.length > 0 ? (
          logs.slice(0, 20).map((evt, idx) => (
            <div key={idx} className="flex items-start gap-2.5 p-2 rounded bg-slate-950/40 border border-slate-800/60 hover:bg-slate-900/60 transition">
              <span className="text-slate-500 shrink-0 font-bold">{evt.timestamp}</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold shrink-0 ${getBadgeColor(evt.level)}`}>
                {evt.category}
              </span>
              <span className="text-slate-400 font-semibold shrink-0">[{evt.event_name}]</span>
              <span className="text-slate-300 truncate">{evt.message}</span>
            </div>
          ))
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs">Awaiting live event telemetry stream...</div>
        )}
      </div>
    </div>
  );
};
