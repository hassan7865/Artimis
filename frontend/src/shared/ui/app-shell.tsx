import Link from "next/link";
import type { ReactNode } from "react";
import { Target } from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Overview" },
  { href: "/leads", label: "Leads" },
  { href: "/settings", label: "Settings" },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-manrope selection:bg-indigo-100 selection:text-indigo-700">
      {/* Decorative background elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-indigo-50/50 blur-[120px]"></div>
        <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] rounded-full bg-blue-50/50 blur-[100px]"></div>
        <div className="absolute -bottom-[5%] left-[20%] w-[25%] h-[25%] rounded-full bg-emerald-50/30 blur-[80px]"></div>
      </div>

      <div className="mx-auto flex w-full max-w-6xl flex-col px-4 py-8 md:px-6">
        <header className="mb-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between bg-white/70 backdrop-blur-md p-6 rounded-3xl border border-white/50 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-600 to-blue-700 flex items-center justify-center shadow-lg shadow-indigo-200">
              <Target className="text-white h-7 w-7" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-600/60 leading-none mb-1">Artemis v1.0</p>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">Lead Engine</h1>
            </div>
          </div>
          <nav className="flex items-center gap-1 bg-slate-100/50 p-1.5 rounded-2xl border border-slate-200/50">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="px-4 py-2 rounded-xl text-sm font-bold text-slate-600 transition hover:bg-white hover:text-slate-900 hover:shadow-sm"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="pb-16">{children}</main>
        
        <footer className="mt-auto py-8 border-t border-slate-200 flex items-center justify-between text-xs font-medium text-slate-400 uppercase tracking-widest">
          <span>&copy; 2026 Artemis AI</span>
          <div className="flex gap-4">
            <span>System Status: Online</span>
            <span>Version: 0.1.0</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
