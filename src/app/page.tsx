import { listLeads } from "@/shared/lib/api";
import Link from "next/link";
import { ScanButton } from "@/shared/ui/scan-button";
import { BarChart3, Flame, Activity, ArrowRight, Zap, Database, Globe } from "lucide-react";
import { SchedulerControls } from "@/shared/ui/scheduler-controls";

export default async function OverviewPage() {
  const payload = await listLeads({ page: 1, pageSize: 5, minScore: 70 });
  const hotLeadsCount = payload.items.filter(l => l.score >= 80).length;

  return (
    <div className="flex flex-col gap-10">
      {/* Stats Section */}
      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="group relative rounded-3xl border border-white bg-white p-8 shadow-xl shadow-slate-200/50 transition hover:scale-[1.02]">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Total Discovery</p>
          <h3 className="mt-2 text-5xl font-black tracking-tighter text-slate-900">{payload.total}</h3>
          <div className="absolute top-8 right-8 text-slate-100 group-hover:text-indigo-100 transition-colors">
            <BarChart3 size={40} strokeWidth={2.5} />
          </div>
        </div>
        
        <div className="group relative rounded-3xl border border-emerald-100 bg-gradient-to-br from-emerald-50 to-white p-8 shadow-xl shadow-emerald-100/20 transition hover:scale-[1.02]">
          <p className="text-[10px] font-black uppercase tracking-widest text-emerald-600/60">High Quality Leads</p>
          <h3 className="mt-2 text-5xl font-black tracking-tighter text-emerald-700">{hotLeadsCount}</h3>
          <div className="absolute top-8 right-8 text-emerald-200 group-hover:text-emerald-400 transition-colors">
            <Flame size={40} strokeWidth={2.5} />
          </div>
        </div>
      </section>

      {/* Scheduler & History Section */}
      <SchedulerControls />

      {/* Recent Leads Section */}
      <section className="rounded-3xl border border-white bg-white/80 p-8 shadow-2xl shadow-slate-200/40 backdrop-blur-sm">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black tracking-tight text-slate-900">Recent Opportunities</h2>
            <p className="text-sm text-slate-500">The most recent leads captured by your monitoring engine.</p>
          </div>
          <Link href="/leads" className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-900 hover:text-white flex items-center gap-2">
            EXPLORE ALL <ArrowRight size={14} />
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {payload.items.map((lead) => (
            <Link 
              key={lead.id} 
              href={`/leads/${lead.id}`}
              className="group flex items-center justify-between rounded-2xl border border-slate-50 bg-slate-50/30 p-5 transition hover:border-indigo-200 hover:bg-white hover:shadow-lg hover:shadow-indigo-100/50"
            >
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-orange-500">r/{lead.subreddit}</span>
                <span className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">{lead.title}</span>
              </div>
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-end">
                  <span className={`text-2xl font-black leading-none ${lead.score >= 80 ? "text-emerald-600" : "text-slate-300"}`}>
                    {lead.score}
                  </span>
                  <span className="text-[8px] font-bold uppercase tracking-widest text-slate-400">SCORE</span>
                </div>
                <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                  <ArrowRight size={18} />
                </div>
              </div>
            </Link>
          ))}
          {payload.items.length === 0 && (
            <div className="py-20 text-center flex flex-col items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-200">
                <Globe size={32} />
              </div>
              <p className="text-slate-500 font-bold italic">Your lead pipeline is currently empty.</p>
            </div>
          )}
        </div>
      </section>
      
      {/* Footer Info */}
      <section className="rounded-3xl bg-gradient-to-r from-slate-900 to-indigo-950 p-10 text-white shadow-2xl">
        <div className="flex flex-col md:flex-row items-center gap-10">
          <div className="flex-1">
            <h2 className="text-3xl font-black tracking-tight">Expand your horizon.</h2>
            <p className="mt-4 text-indigo-100/70 leading-relaxed font-medium">
              Your engine is currently tracking {payload.total} leads. Want to target more niches? 
              Head over to settings to add new keywords and subreddits to your real-time monitor.
            </p>
            <div className="mt-8 flex gap-4">
              <Link href="/settings" className="rounded-xl bg-white px-6 py-3 text-sm font-black text-indigo-950 hover:bg-indigo-50 transition-colors">
                CONFIGURE ENGINE
              </Link>
            </div>
          </div>
          <div className="w-full md:w-auto bg-white/5 rounded-2xl p-6 backdrop-blur-sm border border-white/10 font-mono text-sm text-indigo-200">
            <p className="mb-4 text-white/40 text-[10px] font-bold uppercase tracking-widest flex items-center gap-2">
               <Activity size={12} /> Active Monitor Stats
            </p>
            <div className="space-y-2">
              <p className="flex items-center gap-2"><Zap size={14} className="text-emerald-400" /> Scanner: <span className="text-emerald-400">READY</span></p>
              <p className="flex items-center gap-2"><Activity size={14} /> Protocol: <span className="text-white">Motor-Async</span></p>
              <p className="flex items-center gap-2"><Database size={14} /> Storage: <span className="text-white">MongoDB Atlas</span></p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
