import Link from "next/link";
import { listLeads } from "@/shared/lib/api";
import { Search } from "lucide-react";

export default async function LeadsPage() {
  const payload = await listLeads({ page: 1, pageSize: 50 });

  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Leads Explorer</h1>
          <p className="text-slate-500">Managing {payload.total} leads found across monitored subreddits.</p>
        </div>
      </header>

      <section className="rounded-3xl border border-slate-200 bg-white/50 shadow-xl shadow-slate-100 backdrop-blur-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-200 text-slate-500 uppercase tracking-widest text-[10px] font-bold">
                <th className="px-6 py-4">Topic / Title</th>
                <th className="px-6 py-4">Source</th>
                <th className="px-6 py-4 text-center">Quality</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Discovery Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payload.items.map((lead) => (
                <tr key={lead.id} className="group transition-colors hover:bg-slate-50/80">
                  <td className="px-6 py-5">
                    <Link className="font-bold text-slate-900 hover:text-blue-600 line-clamp-1" href={`/leads/${lead.id}`}>
                      {lead.title}
                    </Link>
                    <p className="mt-0.5 text-xs text-slate-400 line-clamp-1">{lead.body || "No preview available"}</p>
                  </td>
                  <td className="px-6 py-5">
                    <span className="inline-flex items-center rounded-md bg-orange-50 px-2 py-1 text-[10px] font-black text-orange-700 uppercase tracking-tighter">
                      r/{lead.subreddit}
                    </span>
                  </td>
                  <td className="px-6 py-5 text-center">
                    <div className="flex flex-col items-center">
                      <span className={`text-lg font-black ${
                        lead.score >= 80 ? "text-emerald-600" :
                        lead.score >= 50 ? "text-amber-500" :
                        "text-slate-400"
                      }`}>
                        {lead.score}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className={`rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-widest ${
                      lead.status === 'hot' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-500'
                    }`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-6 py-5 text-slate-500 whitespace-nowrap text-xs font-medium">
                    {new Date(lead.found_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {payload.items.length === 0 && (
            <div className="py-20 text-center flex flex-col items-center gap-3">
              <Search className="h-12 w-12 text-slate-200" />
              <p className="text-slate-500 font-medium">No leads found yet. Start a scan to find opportunities.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
