import React, { useEffect, useState } from 'react';
import { SlidersHorizontal, Lock, CheckCircle2 } from 'lucide-react';

export const ParametersView: React.FC = () => {
  const [spot, setSpot] = useState(25400);
  const [ceAvg, setCeAvg] = useState(100);
  const [peAvg, setPeAvg] = useState(95);
  const [lots, setLots] = useState(1);
  const [sl, setSl] = useState(20);
  const [target, setTarget] = useState(40);
  const [overrideLock, setOverrideLock] = useState(false);
  const [version, setVersion] = useState(1);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    const fetchParams = async () => {
      try {
        const res = await fetch('/api/settings/current');
        if (res.ok) {
          const d = await res.json();
          const s = d.settings;
          setSpot(s.reference_spot);
          setCeAvg(s.reference_ce_avg);
          setPeAvg(s.reference_pe_avg);
          setLots(s.lots);
          setSl(s.stop_loss_points);
          setTarget(s.target_points);
          setVersion(s.version || 1);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchParams();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatusMsg('');
    const payload = {
      reference_spot: spot,
      reference_ce_avg: ceAvg,
      reference_pe_avg: peAvg,
      lots,
      stop_loss_points: sl,
      target_points: target
    };

    try {
      const res = await fetch(`/api/settings/update?bypass_lock_for_dev=${overrideLock}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        setStatusMsg(data.message);
        setVersion(data.version);
      } else {
        alert(data.detail);
      }
    } catch (err: any) {
      alert('Error updating parameters: ' + err.message);
    }
  };

  return (
    <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-6 max-w-4xl mx-auto shadow-2xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5 text-blue-400" /> Daily Reference Parameters
          </h2>
          <p className="text-xs text-slate-400 mt-1">Configured daily for Nifty Spot bias and CE/PE condition thresholds.</p>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold px-3 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5 mono">
            <Lock className="w-3.5 h-3.5" /> LOCK WINDOW: 07:30 – 08:00 AM IST
          </span>
          <div className="text-[11px] text-slate-500 mt-1">Current Active: Version {version}</div>
        </div>
      </div>

      {statusMsg ? (
        <div className="mb-4 p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> {statusMsg}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Spot Reference Level</label>
            <input
              type="number"
              step="0.5"
              value={spot}
              onChange={(e) => setSpot(parseFloat(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Compares with 09:15 Spot Open for Bias</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">CE Reference Average</label>
            <input
              type="number"
              step="0.5"
              value={ceAvg}
              onChange={(e) => setCeAvg(parseFloat(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Cond 1 &amp; 2 threshold for CALL</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">PE Reference Average</label>
            <input
              type="number"
              step="0.5"
              value={peAvg}
              onChange={(e) => setPeAvg(parseFloat(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Cond 1 &amp; 2 threshold for PUT</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2 border-t border-slate-800/80">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Lots to Trade</label>
            <input
              type="number"
              min="1"
              max="10"
              value={lots}
              onChange={(e) => setLots(parseInt(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">50 qty per lot for Nifty</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Stop Loss (Points)</label>
            <input
              type="number"
              step="1"
              value={sl}
              onChange={(e) => setSl(parseFloat(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Initial exchange SL placement</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Target (Points)</label>
            <input
              type="number"
              step="1"
              value={target}
              onChange={(e) => setTarget(parseFloat(e.target.value))}
              required
              className="w-full bg-[#070a0f] border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white mono focus:border-blue-500 focus:outline-none"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Profit objective</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="dev-override"
              checked={overrideLock}
              onChange={(e) => setOverrideLock(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0"
            />
            <label htmlFor="dev-override" className="text-xs text-slate-400 cursor-pointer">
              Dev override (permit parameter update outside 07:30–08:00 AM window)
            </label>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-500/20 transition active:scale-95"
          >
            Save &amp; Lock New Version
          </button>
        </div>
      </form>
    </div>
  );
};

