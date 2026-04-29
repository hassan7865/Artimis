export type LeadStatus =
  | "new"
  | "reviewed"
  | "contacted"
  | "replied"
  | "won"
  | "lost"
  | "dismissed";

export type Lead = {
  id: number | string;
  post_id: string;
  subreddit: string;
  title: string;
  body: string | null;
  author: string | null;
  url: string | null;
  upvotes: number;
  score: number;
  intents: string | null;
  matched_keywords: string | null;
  ai_analysis: string | null;
  ai_outreach: string | null;
  status: string | null;
  notified: boolean;
  found_at: string;
  updated_at: string;
};

export type LeadListResponse = {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
};

/** Ignore env pointing at localhost — Next inlines NEXT_PUBLIC_* at build time and breaks SSR/fetch on Vercel */
function usableEnvApiBase(): string | null {
  const raw =
    process.env.NEXT_PUBLIC_ARTEMIS_API_BASE_URL?.trim() ||
    process.env.ARTEMIS_API_BASE_URL?.trim();
  if (!raw) return null;
  const lower = raw.toLowerCase();
  if (lower.includes("localhost") || lower.includes("127.0.0.1")) return null;
  return raw.replace(/\/$/, "");
}

function readRuntimeEnv(key: "VERCEL_URL" | "VERCEL"): string | undefined {
  return process.env[key];
}

function getApiBase(): string {
  const env = usableEnvApiBase();
  if (env) return env;

  if (typeof window !== "undefined") return "";

  // Dynamic lookup so Next does not inline an empty VERCEL_URL from the build machine.
  const v = readRuntimeEnv("VERCEL_URL")?.trim();
  if (v) {
    if (v.startsWith("http://") || v.startsWith("https://")) {
      return v.replace(/\/$/, "");
    }
    return `https://${v}`.replace(/\/$/, "");
  }
  return "http://127.0.0.1:8000";
}

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBase()}${path}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status}): ${path}`);
  }
  return (await response.json()) as T;
}

async function apiPost<T>(path: string, payload: object): Promise<T> {
  const response = await fetch(`${getApiBase()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status}): ${path}`);
  }
  return (await response.json()) as T;
}

export function listLeads(params: {
  page?: number;
  pageSize?: number;
  minScore?: number;
}): Promise<LeadListResponse> {
  const search = new URLSearchParams();
  search.set("page", String(params.page ?? 1));
  search.set("page_size", String(params.pageSize ?? 20));
  if (typeof params.minScore === "number") {
    search.set("min_score", String(params.minScore));
  }
  return apiGet<LeadListResponse>(`/api/leads?${search.toString()}`);
}

export function getLead(id: string): Promise<Lead> {
  return apiGet<Lead>(`/api/leads/${id}`);
}

export function triggerScan(): Promise<{ status: string; message: string }> {
  return apiPost<{ status: string; message: string }>("/api/leads/scan", {});
}

export type AppConfig = {
  keywords: string[];
  subreddits: string[];
  ai_prompt: string | null;
};

export function getConfig(): Promise<AppConfig> {
  return apiGet<AppConfig>("/api/config");
}

export function updateKeywords(items: string[]): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/config/keywords", { items });
}

export function updateSubreddits(items: string[]): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/config/subreddits", { items });
}

export function updateAiPrompt(prompt: string): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/config/prompt", { prompt });
}

export type SchedulerStatus = {
  is_running: boolean;
  interval_minutes: number;
  next_run: string | null;
};

export type ScanLog = {
  id: string;
  new_posts: number;
  leads_found: number;
  duration_sec: number;
  run_at: string;
};

export function getSchedulerStatus(): Promise<SchedulerStatus> {
  return apiGet<SchedulerStatus>("/api/scheduler/status");
}

export function startScheduler(interval: number): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/scheduler/start", { interval_minutes: interval });
}

export function stopScheduler(): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/scheduler/stop", {});
}

export function getScanLogs(): Promise<ScanLog[]> {
  return apiGet<ScanLog[]>("/api/scheduler/logs");
}
