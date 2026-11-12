import { useState } from 'react';
import { Gauge, Receipt, Sliders, BarChart3, ScrollText } from 'lucide-react';
import { useWebSocket } from './hooks/useWebSocket';
import { Header } from './components/Header';
import { MetricCards } from './components/MetricCards';
import { ConditionMatrix } from './components/ConditionMatrix';
import { DecisionJournal } from './components/DecisionJournal';
import { OrdersView } from './components/OrdersView';
import { ParametersView } from './components/ParametersView';
import { ReportsView } from './components/ReportsView';

export function App() {
  const [activeTab, setActiveTab] = useState<'cockpit' | 'orders' | 'parameters' | 'reports' | 'journal'>('cockpit');
  const { state, isConnected } = useWebSocket();

  const handleRefresh = async () => {
    try {
      await fetch('/api/monitor/status');
    } catch (e) {}
  };

  return (
    <div className="bg-[#070a0f] text-slate-100 min-h-screen flex flex-col selection:bg-blue-500/30 selection:text-blue-300">
      
      {/* Top Header & Emergency Controls */}
      <Header state={state} isConnected={isConnected} onRefresh={handleRefresh} />

      {/* Navigation Sub-header */}
      <nav className="border-b border-slate-800/80 bg-[#090d14] px-5 shadow-sm">
        <div className="max-w-[1700px] mx-auto flex items-center gap-2 overflow-x-auto text-xs font-semibold py-2">
          
          <button
            onClick={() => setActiveTab('cockpit')}
            className={`px-3.5 py-1.5 rounded-md flex items-center gap-2 transition ${
              activeTab === 'cockpit'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Gauge className="w-4 h-4" /> Live Cockpit
          </button>

          <button
            onClick={() => setActiveTab('orders')}
            className={`px-3.5 py-1.5 rounded-md flex items-center gap-2 transition ${
              activeTab === 'orders'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Receipt className="w-4 h-4" /> Orders &amp; Positions
          </button>

          <button
            onClick={() => setActiveTab('parameters')}
            className={`px-3.5 py-1.5 rounded-md flex items-center gap-2 transition ${
              activeTab === 'parameters'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Sliders className="w-4 h-4" /> Daily Parameters (07:30-08:00)
          </button>

          <button
            onClick={() => setActiveTab('reports')}
            className={`px-3.5 py-1.5 rounded-md flex items-center gap-2 transition ${
              activeTab === 'reports'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <BarChart3 className="w-4 h-4" /> Performance Reports
          </button>

          <button
            onClick={() => setActiveTab('journal')}
            className={`px-3.5 py-1.5 rounded-md flex items-center gap-2 transition ${
              activeTab === 'journal'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <ScrollText className="w-4 h-4" /> Decision Journal &amp; Audit
          </button>

        </div>
      </nav>

      {/* Main Container */}
      <main className="flex-1 max-w-[1700px] w-full mx-auto p-5 space-y-5">
        {activeTab === 'cockpit' && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <MetricCards state={state} />
            <ConditionMatrix ce={state?.ce} pe={state?.pe} />
            <DecisionJournal logs={state?.event_journal} />
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="animate-in fade-in duration-200">
            <OrdersView />
          </div>
        )}

        {activeTab === 'parameters' && (
          <div className="animate-in fade-in duration-200">
            <ParametersView />
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="animate-in fade-in duration-200">
            <ReportsView />
          </div>
        )}

        {activeTab === 'journal' && (
          <div className="animate-in fade-in duration-200">
            <div className="bg-[#0c111c] border border-slate-800 rounded-2xl p-5 shadow-xl">
              <h2 className="text-sm font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
                <ScrollText className="w-4 h-4 text-blue-400" /> Full Chronological Decision Journal &amp; Audit Logs
              </h2>
              <div className="space-y-2.5 max-h-[650px] overflow-y-auto custom-scrollbar font-mono text-xs">
                {state?.event_journal && state.event_journal.length > 0 ? (
                  state.event_journal.map((l, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800 hover:bg-slate-900/60 transition">
                      <span className="text-slate-500 font-bold shrink-0">{l.timestamp}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                        l.level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                        l.level === 'WARNING' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                        'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                      }`}>
                        {l.category}
                      </span>
                      <span className="text-slate-400 font-bold shrink-0">[{l.event_name}]</span>
                      <span className="text-slate-200">{l.message}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-10 text-slate-500">No events logged yet.</div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900/90 py-3 px-5 text-center text-xs text-slate-500 bg-[#090d14]">
        <span>TradeBot 1.0 &bull; Angel One SmartAPI Integration &bull; Deterministic Options Execution Engine</span>
      </footer>

    </div>
  );
}

export default App;
