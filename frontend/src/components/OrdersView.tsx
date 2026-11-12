import React, { useEffect, useState } from 'react';
import { FileText, Wallet } from 'lucide-react';
import type { OrderItem, ClosedPosition } from '../types';

export const OrdersView: React.FC = () => {
  const [orders, setOrders] = useState<OrderItem[]>([]);
  const [closed, setClosed] = useState<ClosedPosition[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordRes, posRes] = await Promise.all([
          fetch('/api/orders/list'),
          fetch('/api/orders/positions')
        ]);
        if (ordRes.ok) setOrders(await ordRes.json());
        if (posRes.ok) {
          const posData = await posRes.json();
          setClosed(posData.closed || []);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Orders Ledger */}
      <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-400" /> Orders Ledger (Angel One SmartAPI)
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Time</th>
                <th className="p-3">Order ID</th>
                <th className="p-3">Purpose</th>
                <th className="p-3">Symbol</th>
                <th className="p-3">Side</th>
                <th className="p-3">Type</th>
                <th className="p-3">Qty</th>
                <th className="p-3">Price</th>
                <th className="p-3">Trigger</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {orders.map((o, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition">
                  <td className="p-3 text-slate-400">{o.time}</td>
                  <td className="p-3 text-slate-300 font-bold">{o.order_id}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {o.purpose}
                    </span>
                  </td>
                  <td className="p-3 text-white font-bold">{o.symbol}</td>
                  <td className={`p-3 font-bold ${o.side === 'BUY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {o.side}
                  </td>
                  <td className="p-3 text-slate-400">{o.type}</td>
                  <td className="p-3 text-white">{o.qty}</td>
                  <td className="p-3 text-slate-300">{o.price ? `₹${o.price.toFixed(2)}` : '--'}</td>
                  <td className="p-3 text-slate-400">{o.trigger_price ? `₹${o.trigger_price.toFixed(2)}` : '--'}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.status === 'FILLED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}>
                      {o.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Closed Positions */}
      <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
          <Wallet className="w-4 h-4 text-emerald-400" /> Closed Positions & Realized P&L
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Date</th>
                <th className="p-3">Symbol</th>
                <th className="p-3">Qty</th>
                <th className="p-3">Entry</th>
                <th className="p-3">Exit</th>
                <th className="p-3">Exit Reason</th>
                <th className="p-3">Gross P&L</th>
                <th className="p-3">Charges (STT/Bkr)</th>
                <th className="p-3">Net P&L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {closed.map((p, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition">
                  <td className="p-3 text-slate-400">{p.date}</td>
                  <td className="p-3 text-white font-bold">{p.symbol}</td>
                  <td className="p-3">{p.quantity}</td>
                  <td className="p-3 text-slate-300">₹{p.entry_price.toFixed(2)}</td>
                  <td className="p-3 text-slate-300">₹{p.exit_price.toFixed(2)}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {p.exit_reason}
                    </span>
                  </td>
                  <td className={`p-3 font-bold ${p.gross_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ₹{p.gross_pnl.toFixed(2)}
                  </td>
                  <td className="p-3 text-slate-400">₹{p.charges.toFixed(2)}</td>
                  <td className={`p-3 font-extrabold ${p.net_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ₹{p.net_pnl.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
