"use client";

import { useState } from "react";
import { triggerScan } from "@/shared/lib/api";
import { RefreshCcw } from "lucide-react";

export function ScanButton() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleScan = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await triggerScan();
      setStatus(res.message);
      // Auto-hide status after 5 seconds
      setTimeout(() => setStatus(null), 5000);
    } catch (error) {
      setStatus("Failed to trigger scan. Make sure the API is running.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-end gap-2 w-full">
      <button
        onClick={handleScan}
        disabled={loading}
        className={`w-full inline-flex items-center justify-center rounded-xl px-6 py-2.5 text-sm font-bold text-white shadow-sm transition ${
          loading ? "bg-slate-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700 active:scale-95 shadow-indigo-200"
        }`}
      >
        {loading ? (
          <>
            <RefreshCcw className="mr-2 h-4 w-4 animate-spin" />
            Scanning...
          </>
        ) : (
          <>
            <RefreshCcw className="mr-2 h-4 w-4" />
            Run Fresh Scan
          </>
        )}
      </button>
      {status && (
        <p className={`text-[10px] font-medium ${status.includes("Failed") ? "text-red-500" : "text-emerald-600"}`}>
          {status}
        </p>
      )}
    </div>
  );
}
