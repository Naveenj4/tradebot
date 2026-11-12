import React from 'react';
import { Zap, ShieldCheck, PauseCircle, PlayCircle, XCircle, AlertOctagon, Wifi, WifiOff } from 'lucide-react';
import type { TelemetryState } from '../types';

interface HeaderProps {
  state: TelemetryState | null;
  isConnected: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ state, isConnected, onRefresh }) => {
  const isPaused = state?.is_paused ?? false;
  const isKillSwitch = state?.kill_switch_active ?? false;
  const fsmState = state?.fsm_state ?? 'WAITING_MARKET_OPEN';
  const brokerName = state?.broker_name ?? 'ANGELONE';
  const tradeMode = state?.trade_mode ?? 'PAPER';

  const handleTogglePause = async () => {
    const endpoint = isPaused ? '/api/control/resume' : '/api/control/pause';
    await fetch(endpoint, { method: 'POST' });
    onRefresh();
  };

  const handleManualSquareOff = async () => {
    if (confirm('Square off active position at market immediately?')) {
      const res = await fetch('/api/control/square-off', { method: 'POST' });
      const data = await res.json();
      alert(data.message);
      onRefresh();
    }
  };

  const handleKillSwitch = async () => {
    if (confirm('🛑 EMERGENCY KILL SWITCH: Are you sure? All orders will cancel and open positions will be squared off instantly.')) {
      const res = await fetch('/api/control/kill-switch', { method: 'POST' });
      const data = await res.json();
      alert(data.action);
      onRefresh();
    }
  };

  const handleResetKillSwitch = async () => {
    if (confirm('Reset emergency kill switch and restore standby?')) {
      await fetch('/api/control/reset-kill-switch', { method: 'POST' });
      onRefresh();
    }
  };

  return (
    <header className="border-b border-slate-800/80 bg-[#0c111c]/95 backdrop-blur sticky top-0 z-50 px-5 py-3 shadow-lg">
      <div className="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-4">
        
        {/* Brand & Market Session */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-extrabold tracking-tight text-white">TradeBot</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold mono">REACT-VITE</span>
              </div>
              <div className="text-[10px] text-slate-400 font-medium tracking-wide">NSE NIFTY OPTIONS &bull; 09:15-09:20 TRIGGER</div>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-800 hidden sm:block"></div>

          {/* Engine Status Pills */}
          <div className="flex items-center gap-2 text-xs flex-wrap">
            <div className={`px-2.5 py-1 rounded-md border font-bold flex items-center gap-1.5 mono ${
              isKillSwitch 
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-400' 
                : isPaused
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-400'
                : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isKillSwitch ? 'bg-rose-400' : isPaused ? 'bg-amber-400' : 'bg-emerald-400 animate-pulse-subtle'}`}></span>
              <span>{fsmState}</span>
            </div>

            <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700/60 text-slate-300 font-semibold flex items-center gap-1.5 mono">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
              <span>{brokerName.toUpperCase()} (SMARTAPI)</span>
            </div>

            <div className={`px-2.5 py-1 rounded-md border font-bold mono ${
              tradeMode === 'LIVE' ? 'bg-rose-500/15 border-rose-500/30 text-rose-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
            }`}>
              <span>{tradeMode === 'LIVE' ? 'LIVE MODE' : 'PAPER MODE'}</span>
            </div>

            <div className="px-2 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-400 flex items-center gap-1 mono text-[11px]">
              {isConnected ? <Wifi className="w-3 h-3 text-emerald-400" /> : <WifiOff className="w-3 h-3 text-rose-400" />}
              <span>{isConnected ? 'WS LIVE' : 'CONNECTING'}</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {isKillSwitch ? (
            <button
              onClick={handleResetKillSwitch}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 transition active:scale-95 shadow-lg shadow-emerald-900/30"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Reset Kill Switch</span>
            </button>
          ) : null}

          <button
            onClick={handleTogglePause}
            className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition active:scale-95"
          >
            {isPaused ? <PlayCircle className="w-3.5 h-3.5 text-emerald-400" /> : <PauseCircle className="w-3.5 h-3.5 text-amber-400" />}
            <span>{isPaused ? 'Resume Bot' : 'Pause Bot'}</span>
          </button>

          <button
            onClick={handleManualSquareOff}
            className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition active:scale-95"
          >
            <XCircle className="w-3.5 h-3.5 text-orange-400" />
            <span>Square Off</span>
          </button>

          <button
            onClick={handleKillSwitch}
            className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-rose-900/40 transition active:scale-95"
          >
            <AlertOctagon className="w-3.5 h-3.5" />
            <span>KILL SWITCH</span>
          </button>
        </div>

      </div>
    </header>
  );
};
