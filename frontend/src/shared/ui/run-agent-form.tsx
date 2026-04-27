"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import {
  executeRun,
  type ExecuteRunResponse,
  type ModeName,
  type SourceCatalogItem,
  type SourceName,
} from "@/shared/lib/api";

const MODE_OPTIONS: Array<{ value: ModeName; label: string; hint: string }> = [
  {
    value: "agency_leads",
    label: "Agency Leads",
    hint: "Find buying-intent signals for AI automation services.",
  },
  {
    value: "jobs",
    label: "Jobs",
    hint: "Find full-time company openings across global job platforms.",
  },
  {
    value: "outbound",
    label: "Outbound",
    hint: "Find companies by sector and location for outreach campaigns.",
  },
];

type RunAgentFormProps = {
  sources: SourceCatalogItem[];
  initialMode?: ModeName;
  lockMode?: boolean;
  heading?: string;
  subheading?: string;
  initialSearchQuery?: string;
  initialLocation?: string;
};

export function RunAgentForm({
  sources,
  initialMode = "agency_leads",
  lockMode = false,
  heading = "Run Multi-Source Agent",
  subheading = "Select mode, query, location, and source platforms. The backend runs each platform and stores leads with score and contact details.",
  initialSearchQuery = "voice ai automation",
  initialLocation = "Dubai",
}: RunAgentFormProps) {
  const [mode, setMode] = useState<ModeName>(initialMode);
  const [searchQuery, setSearchQuery] = useState(initialSearchQuery);
  const [location, setLocation] = useState(initialLocation);
  const [maxResultsPerSource, setMaxResultsPerSource] = useState(8);
  const [selectedSources, setSelectedSources] = useState<SourceName[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExecuteRunResponse | null>(null);

  const modeSources = useMemo(
    () => sources.filter((source) => source.modes.includes(mode)),
    [mode, sources],
  );

  function toggleSource(name: SourceName) {
    setSelectedSources((current) =>
      current.includes(name) ? current.filter((item) => item !== name) : [...current, name],
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setIsSubmitting(true);

    try {
      const payload = await executeRun({
        mode,
        search_query: searchQuery,
        location: location || undefined,
        max_results_per_source: maxResultsPerSource,
        sources: selectedSources.length > 0 ? selectedSources : undefined,
      });
      setResult(payload);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unknown error while running agent.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Execution</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight">{heading}</h2>
        <p className="mt-2 text-sm text-slate-600">{subheading}</p>
      </div>

      <form className="grid gap-5" onSubmit={onSubmit}>
        <div className="grid gap-2">
          <label className="text-sm font-medium text-slate-800" htmlFor="searchQuery">
            Search query
          </label>
          <input
            id="searchQuery"
            className="rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-slate-900"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="voice ai, automation agency, full-stack engineer"
            required
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {lockMode ? (
            <div className="grid gap-2">
              <label className="text-sm font-medium text-slate-800">Mode</label>
              <div className="rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm">
                {MODE_OPTIONS.find((option) => option.value === mode)?.label}
              </div>
              <p className="text-xs text-slate-500">
                {MODE_OPTIONS.find((option) => option.value === mode)?.hint}
              </p>
            </div>
          ) : (
            <div className="grid gap-2">
              <label className="text-sm font-medium text-slate-800" htmlFor="mode">
                Mode
              </label>
              <select
                id="mode"
                className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-900"
                value={mode}
                onChange={(event) => {
                  setMode(event.target.value as ModeName);
                  setSelectedSources([]);
                }}
              >
                {MODE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-slate-500">
                {MODE_OPTIONS.find((option) => option.value === mode)?.hint}
              </p>
            </div>
          )}

          <div className="grid gap-2">
            <label className="text-sm font-medium text-slate-800" htmlFor="location">
              Location filter
            </label>
            <input
              id="location"
              className="rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-slate-900"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="City, country, or remote"
            />
          </div>
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium text-slate-800" htmlFor="maxResults">
            Max results per source
          </label>
          <input
            id="maxResults"
            type="number"
            min={1}
            max={50}
            className="w-44 rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-slate-900"
            value={maxResultsPerSource}
            onChange={(event) => setMaxResultsPerSource(Number(event.target.value))}
          />
        </div>

        <div className="grid gap-3">
          <p className="text-sm font-medium text-slate-800">Sources (optional override)</p>
          <div className="grid gap-2 md:grid-cols-2">
            {modeSources.map((source) => {
              const checked = selectedSources.includes(source.name);
              return (
                <label
                  key={source.name}
                  className="flex cursor-pointer gap-3 rounded-xl border border-slate-200 p-3"
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleSource(source.name)}
                    className="mt-1"
                  />
                  <span>
                    <span className="block text-sm font-medium text-slate-900">{source.name}</span>
                    <span className="mt-1 block text-xs text-slate-600">{source.description}</span>
                  </span>
                </label>
              );
            })}
          </div>
          <p className="text-xs text-slate-500">
            If no source is selected, the backend uses default sources for the chosen mode.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-60"
          >
            {isSubmitting ? "Running..." : "Run Agent"}
          </button>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </div>
      </form>

      {result ? (
        <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm">
          <p className="font-semibold text-emerald-900">Run completed</p>
          <p className="mt-1 text-emerald-800">
            Created {result.created_leads} leads across {result.run.sources.length} source runs.
          </p>
          <div className="mt-3 flex gap-3">
            <Link className="underline" href={`/runs/${result.run.id}`}>
              Open run details
            </Link>
            <Link className="underline" href="/leads">
              Open leads
            </Link>
          </div>
        </div>
      ) : null}
    </section>
  );
}
