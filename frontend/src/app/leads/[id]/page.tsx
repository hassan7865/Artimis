import { getLead } from "@/shared/lib/api";
import Link from "next/link";
import { ChevronLeft, ExternalLink, Cpu, PenTool, Hash, Info, Copy } from "lucide-react";

interface PageProps {
  params: { id: string };
}

export default async function LeadDetailPage({ params }: PageProps) {
  const { id } = await params;
  const lead = await getLead(id);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Link href="/leads" className="flex items-center gap-1 hover:text-slate-900 transition-colors">
          <ChevronLeft size={14} /> Leads
        </Link>
        <span>/</span>
        <span className="text-slate-900 font-medium">{lead.post_id}</span>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column: Post Content */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="mb-6 flex items-start justify-between gap-4">
              <h1 className="text-3xl font-black tracking-tight text-slate-900">{lead.title}</h1>
              <div className="flex flex-col items-end">
                <span className={`text-4xl font-black ${
                  lead.score >= 80 ? "text-emerald-600" : lead.score >= 50 ? "text-amber-500" : "text-slate-400"
                }`}>
                  {lead.score}
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">Quality Score</span>
              </div>
            </div>

            <div className="mb-8 flex flex-wrap gap-2">
              <span className="rounded-xl bg-orange-50 px-3 py-1.5 text-xs font-black text-orange-700 uppercase">r/{lead.subreddit}</span>
              <span className="rounded-xl bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600">By {lead.author}</span>
              <span className="rounded-xl bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600">{lead.upvotes} Upvotes</span>
              {lead.status && <span className="rounded-xl bg-indigo-50 px-3 py-1.5 text-xs font-black text-indigo-600 uppercase tracking-widest">{lead.status}</span>}
            </div>

            <div className="prose prose-slate max-w-none border-t border-slate-100 pt-8">
              <p className="whitespace-pre-wrap text-slate-700 leading-relaxed text-lg">
                {lead.body || "No body content provided."}
              </p>
            </div>
            
            <div className="mt-10">
              <a 
                href={lead.url || "#"} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-8 py-4 text-sm font-black text-white transition hover:bg-slate-800 hover:scale-[1.02] active:scale-95"
              >
                View on Reddit <ExternalLink size={16} />
              </a>
            </div>
          </section>

          {/* AI Analysis section */}
          {lead.ai_analysis && (
            <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="mb-6 text-xl font-black text-slate-900 flex items-center gap-3">
                <Cpu className="text-indigo-600" /> AI Analysis
              </h2>
              <div className="rounded-2xl bg-slate-50 p-6 text-slate-800 italic leading-relaxed text-lg border border-slate-100">
                "{lead.ai_analysis}"
              </div>
            </section>
          )}
        </div>

        {/* Right Column: Outreach & Metadata */}
        <div className="flex flex-col gap-6">
          <section className="rounded-3xl border border-slate-200 bg-indigo-600 p-8 text-white shadow-xl shadow-indigo-200">
            <h2 className="mb-6 text-xl font-black flex items-center gap-3">
              <PenTool /> Outreach Draft
            </h2>
            <div className="mb-8 rounded-2xl bg-white/10 p-6 text-sm font-medium leading-relaxed backdrop-blur-sm border border-white/10">
              {lead.ai_outreach || "No outreach draft generated."}
            </div>
            <button className="w-full flex items-center justify-center gap-2 rounded-2xl bg-white py-4 text-sm font-black text-indigo-600 transition hover:bg-indigo-50 hover:scale-[1.02] active:scale-95">
              <Copy size={16} /> Copy Draft
            </button>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="mb-6 text-xs font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2">
              <Hash size={14} /> Keywords & Intents
            </h2>
            <div className="flex flex-wrap gap-2">
              {lead.intents && JSON.parse(lead.intents.replace(/'/g, '"')).map((intent: string) => (
                <span key={intent} className="rounded-xl bg-emerald-50 px-3 py-1.5 text-xs font-black text-emerald-700 uppercase">
                  {intent}
                </span>
              ))}
              {lead.matched_keywords && JSON.parse(lead.matched_keywords.replace(/'/g, '"')).map((kw: string) => (
                <span key={kw} className="rounded-xl bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600">
                  {kw}
                </span>
              ))}
            </div>
          </section>
          
          <div className="flex items-center justify-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <Info size={12} /> Found on {new Date(lead.found_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
