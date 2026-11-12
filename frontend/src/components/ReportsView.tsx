import React, { useEffect, useState } from 'react';
import { Download, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import type { PerformanceReport } from '../types';

export const ReportsView: React.FC = () => {
  const [report, setReport] = useState<PerformanceReport | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await fetch('/api/reports/summary');
        if (res.ok) setReport(await res.json());
      } catch (e) {
        console.error(e);
      }
    };
    fetchReport();
  }, []);

  const m = report?.metrics;
  const equityData = report?.equity_curve || [];

  return (
    <div className="space-y-6">
      
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl shadow-md">
          <div className="text-[10px] uppercase font-bold text-slate-400">Win Rate</div>
          <div className="text-2xl font-black text-emerald-400 mono mt-1">
            {m?.win_rate_pct ?? 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            {m?.winning_trades ?? 0} Wins &bull; {m?.losing_trades ?? 0} Losses
          </div>
        </div>

        <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl shadow-md">
          <div className="text-[10px] uppercase font-bold text-slate-400">Profit Factor</div>
          <div className="text-2xl font-black text-blue-400 mono mt-1">
            {m?.profit_factor ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Gross Win / Gross Loss</div>
        </div>

        <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl shadow-md">
          <div className="text-[10px] uppercase font-bold text-slate-400">Total Net P&amp;L</div>
          <div className={`text-2xl font-black mono mt-1 ${(m?.net_pnl ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {(m?.net_pnl ?? 0) >= 0 ? '+' : ''}₹{m?.net_pnl?.toFixed(2) ?? '0.00'}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">After brokerage &amp; STT</div>
        </div>

        <div className="bg-[#0c111c] border border-slate-800 p-4 rounded-xl shadow-md">
          <div className="text-[10px] uppercase font-bold text-slate-400">Max Drawdown</div>
          <div className="text-2xl font-black text-rose-400 mono mt-1">
            ₹{m?.max_drawdown?.toFixed(2) ?? '0.00'}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Peak-to-trough decline</div>
        </div>
      </div>

      {/* Equity Curve Chart */}
      <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" /> Cumulative Equity Growth (INR)
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={equityData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${v}`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val: any) => [`₹${Number(val).toFixed(2)}`, 'Cumulative P&L']}
              />
              <Area type="monotone" dataKey="cumulative" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#equityGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Export Strip */}
      <div className="flex items-center justify-between bg-[#0c111c] border border-slate-800 p-4 rounded-xl shadow-md">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">Full Regulatory &amp; Audit Trail Export</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Exports every trade with exact fill price, slippage, charges, and exit reason.</p>
        </div>
        <a
          href="/api/reports/export-csv"
          download
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-900/30 transition active:scale-95"
        >
          <Download className="w-3.5 h-3.5" /> Export CSV Records
        </a>
      </div>

    </div>
  );
};
