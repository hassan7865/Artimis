"use client";

import { useEffect, useState } from "react";
import { getSchedulerStatus, startScheduler, stopScheduler, getScanLogs, SchedulerStatus, ScanLog } from "@/shared/lib/api";
import { Play, Square, Clock, History, RefreshCcw, Search, Zap, CheckCircle2 } from "lucide-react";

export function SchedulerControls() {
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [logs, setLogs] = useState<ScanLog[]>([]);
  const [interval, setIntervalValue] = useState<number>(60);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [s, l] = await Promise.all([getSchedulerStatus(), getScanLogs()]);
      setStatus(s);
      setLogs(l);
      if (s.interval_minutes) setIntervalValue(s.interval_minutes);
    } catch (e) {
      console.error("Failed to fetch scheduler data", e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStart = async () => {
    setLoading(true);
    try {
      await startScheduler(interval);
      await fetchData();
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopScheduler();
      await fetchData();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
      {/* Controls Card */}
      <div className="rounded-3xl border border-white bg-white p-8 shadow-xl shadow-slate-200/50">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-black tracking-tight text-slate-900 flex items-center gap-2">
            <Zap size={20} className="text-indigo-600" />
            SCANNER ENGINE
          </h2>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${status?.is_running ? "bg-emerald-500 animate-pulse" : "bg-slate-300"}`}></div>
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
              {status?.is_running ? "Scheduled" : "Idle"}
            </span>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2 block">
              Scan Interval (Minutes)
            </label>
            <div className="flex items-center gap-3">
              <div className="relative flex-1">
                <Clock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                <input 
                  type="number" 
                  value={isNaN(interval) ? "" : interval}
                  onChange={(e) => {
                    const val = parseInt(e.target.value);
                    setIntervalValue(isNaN(val) ? 0 : val);
                  }}
                  disabled={status?.is_running}
                  className="w-full rounded-2xl border border-slate-100 bg-slate-50 py-3 pl-12 pr-4 font-bold text-slate-900 outline-none transition focus:border-indigo-300 focus:bg-white disabled:opacity-50"
                  placeholder="Minutes..."
                />
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            {status?.is_running ? (
              <button 
                onClick={handleStop}
                disabled={loading}
                className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-rose-50 px-6 py-4 font-black text-rose-600 transition hover:bg-rose-100 disabled:opacity-50"
              >
                <Square size={18} fill="currentColor" /> STOP ENGINE
              </button>
            ) : (
              <button 
                onClick={handleStart}
                disabled={loading}
                className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-6 py-4 font-black text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
              >
                <Play size={18} fill="currentColor" /> START ENGINE
              </button>
            )}
          </div>

          {status?.next_run && (
            <p className="text-center text-[10px] font-bold italic text-slate-400">
              Next scan scheduled for: {new Date(status.next_run).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      {/* Logs Card */}
      <div className="rounded-3xl border border-white bg-white p-8 shadow-xl shadow-slate-200/50">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-black tracking-tight text-slate-900 flex items-center gap-2">
            <History size={20} className="text-indigo-600" />
            SCAN HISTORY
          </h2>
          <button onClick={fetchData} className="text-slate-400 hover:text-indigo-600 transition-colors">
            <RefreshCcw size={16} />
          </button>
        </div>

        <div className="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="flex items-center justify-between rounded-2xl border border-slate-50 bg-slate-50/50 p-4 transition hover:bg-white hover:shadow-md">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-slate-900 italic">
                      {new Date(log.run_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <span className="text-[10px] font-bold text-slate-400">
                      {new Date(log.run_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1 text-[10px] font-bold text-slate-500">
                      <Search size={10} /> {log.new_posts} Checked
                    </span>
                    <span className="flex items-center gap-1 text-[10px] font-black text-emerald-600">
                      <CheckCircle2 size={10} /> {log.leads_found} Leads
                    </span>
                  </div>
                </div>
                <div className="text-[10px] font-black text-slate-300">
                  {log.duration_sec}s
                </div>
              </div>
            ))}
            {logs.length === 0 && (
              <div className="py-10 text-center text-[10px] font-bold italic text-slate-400">
                No scan history available yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
