# Lead Engine Frontend

**Next.js 16** dashboard for the Lead Engine internal tool.

Single-page application providing full visibility into the lead generation pipeline: browse scored leads, review run history, configure mode parameters, trigger manual executions, and manage API credentials.

---

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

The frontend expects the backend API at `http://127.0.0.1:8000`. Override with:

```bash
# frontend/.env.local
NEXT_PUBLIC_ARTEMIS_API_BASE_URL=http://127.0.0.1:8000
```

---

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript + React 19
- **Styling:** Tailwind CSS v4
- **Components:** shadcn/ui (unstyled primitives built with Tailwind)
- **Data Fetching:** Native `fetch()` in Server Components + client-side mutations
- **State Management:** React Server Components + minimal client state

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router (file-based routing)
│   │   ├── page.tsx                     # Overview dashboard (aggregated stats)
│   │   ├── agent/page.tsx               # Generic multi-mode runner
│   │   ├── job-finder/page.tsx          # Jobs-specific portal
│   │   ├── outbound/page.tsx            # Outbound-specific portal
│   │   ├── leads/                       # Lead management
│   │   │   ├── page.tsx                 # Filterable lead table
│   │   │   └── [id]/page.tsx           # Lead detail view
│   │   ├── runs/                        # Run tracking
│   │   │   ├── page.tsx                 # Run history
│   │   │   └── [id]/page.tsx           # Per-source run breakdown
│   │   ├── sources/page.tsx             # Source catalog (health + config)
│   │   ├── modes/                       # Mode configuration
│   │   │   ├── page.tsx                 # List of all modes
│   │   │   └── [name]/page.tsx         # YAML editor + manual trigger
│   │   └── settings/page.tsx            # API key management
│   │
│   ├── shared/
│   │   ├── lib/api.ts           # Type-safe API client (mirrors backend Pydantic models)
│   │   └── ui/
│   │       ├── app-shell.tsx    # Navigation sidebar + layout wrapper
│   │       └── run-agent-form.tsx  # Reusable execution form component
│   │
│   └── globals.css              # Tailwind imports + global resets
│
├── package.json                 # Next.js, React, Tailwind, ESLint
├── postcss.config.mjs            # Tailwind CSS processor
├── tsconfig.json                 # TypeScript configuration
├── next.config.mjs               # Next.js configuration
└── README.md                    # (this file)
```

---

## Routes

| Route | Purpose |
|---|---|
| `/` | Overview: aggregated stats (new leads, recent runs, top scored) |
| `/agent` | Generic runner: select any mode + customize query/location + pick sources |
| `/job-finder` | Jobs portal: focused on AI/ML/full-stack roles with preset defaults |
| `/outbound` | Outbound portal: Google Maps-based business prospecting |
| `/leads` | Filterable table across all modes — status, score, source, date |
| `/leads/[id]` | Full lead detail: raw content, enrichment, score reasoning, status timeline |
| `/runs` | Run history per mode — timing, cost, lead count |
| `/runs/[id]` | Per-source breakdown: fetched → after_dedup → after_filter → enriched → scored → persisted |
| `/sources` | Source catalog — health status, rate limits, last success/failure |
| `/modes` | List of configured modes with enable/disable toggles |
| `/modes/[name]` | YAML editor (Monaco) with schema validation + manual run trigger |
| `/settings` | API key management (stored in backend DB, not frontend env) |

Navigation shell (`app-shell.tsx`) links all routes.

---

## API Client

**`src/shared/lib/api.ts`**

Centralized, type-safe wrapper around the FastAPI backend. Domain types mirror backend Pydantic models:

```typescript
export type Lead = {
  id: string
  mode: "agency_leads" | "jobs" | "outbound"
  status: LeadStatus
  score: number
  raw: { source_name: string; content: string; ... }
  enrichment: { company_name?: string; contacts: Contact[]; ... }
  ...
}

export type RunRecord = {
  id: string
  mode: string
  status: "pending" | "running" | "succeeded" | "failed"
  start_time: string
  end_time?: string
  llm_cost_usd?: number
  source_stats: SourceRunStat[]
  ...
}

// API functions
export async function listLeads(params?: LeadListParams): Promise<Lead[]>
export async function getLead(id: string): Promise<Lead>
export async function updateLeadStatus(id: string, status: LeadStatus): Promise<void>
export async function listRuns(limit?: number): Promise<RunRecord[]>
export async function executeRun(payload: ExecuteRunPayload): Promise<RunRecord>
export async function listSources(): Promise<SourceCatalogItem[]>
export async function getMode(name: string): Promise<ModeConfig>
export async function updateMode(name: string, yaml: string): Promise<void>
```

Base URL resolution order:
1. `NEXT_PUBLIC_ARTEMIS_API_BASE_URL` env var
2. Fallback to `http://127.0.0.1:8000` (local dev default)

---

## Component Patterns

### Reusable `RunAgentForm`

Found at `src/shared/ui/run-agent-form.tsx`. Used by both the generic `/agent` page and the dedicated portal pages (`/job-finder`, `/outbound`).

**Props:**
```typescript
interface RunAgentFormProps {
  initialMode?: string
  lockMode?: boolean   // if true, mode selector hidden
  title?: string
  description?: string
  defaultQuery?: string
  defaultLocation?: string
  sourcesOverrides?: string[]  // pre-checked sources
}
```

**Behavior:**
- On submit → POST `/api/runs/execute`
- Polls `/api/runs/[id]` every 2s until completion
- Shows progress + per-source stats when complete
- Links to `/runs/[id]` and `/leads` results

### Portal Page Pattern

Pages like `/job-finder` and `/outbound` are mode-specific lenses:

```typescript
// Example: /job-finder/page.tsx
export default async function JobFinderPage() {
  // Server-side: fetch source catalog + recent jobs
  const [sources, recentLeads] = await Promise.all([
    listSources(),
    listLeads({ mode: "jobs", limit: 10 }),
  ])

  return (
    <div className="flex gap-6">
      {/* Left panel: execution form */}
      <section className="w-1/3">
        <RunAgentForm
          initialMode="jobs"
          lockMode={true}
          title="Job Finder"
          description="Monitor full-time AI/ML/eng roles"
        />
      </section>

      {/* Right panel: recent results */}
      <section className="w-2/3">
        <LeadTable leads={recentLeads} />
      </section>
    </div>
  )
}
```

Server-side reads mean no loading spinners for initial page render. Form submission is client-side only.

---

## Styling

**Tailwind CSS v4** with `@tailwindcss/postcss` plugin.

- Utility-first classes (e.g. `flex`, `p-4`, `text-sm`, `rounded-lg`)
- **shadcn/ui** components for primitives: `Button`, `Card`, `Table`, `Dialog`, `Form`, `Input`, `Select`, `Textarea`
- Global styles in `src/globals.css` — imports Tailwind, sets font family (Geist via `next/font`)

No CSS modules. All styling via Tailwind utilities + component props.

---

## Development Commands

From `frontend/` directory:

```bash
# Development server (hot reload)
npm run dev

# Lint
npm run lint

# Build for production
npm run build

# Start production server locally
npm run start
```

**Pre-commit checklist:**
1. `npm run lint` — zero errors
2. `npm run build` — successful static generation (if applicable)
3. Test pages in `http://localhost:3000` after `npm run dev`

---

## TypeScript Configuration

`tsconfig.json` targets ES2022, strict mode enabled:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "ES2022"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }]
  }
}
```

---

## Data Fetching Strategy

**Server Components for reads** — Pages fetch data at request time using `async/await` directly in React components. No `useEffect` needed for primary content.

**Client Components for mutations** — Forms (`RunAgentForm`) are `"use client"` and call API directly. Results update client-side only; full page refresh shows fresh data from server.

**Cache invalidation:** For V1, no sophisticated caching. Frontend always fetches fresh data on page load. Future: TanStack Query could be added for optimistic updates.

---

## Error Handling

API errors follow RFC 7807 Problem Details format. The API client (`api.ts`) does not throw on non-2xx; instead, it:

- Returns `null` or empty array for GET failures
- Throws for POST/PATCH failures (after logging error to console)

UI shows toast notifications (using `sonner` or `react-hot-toast`) for:

- Run submission success/failure
- Lead status update failures
- Mode config validation errors

Currently, errors appear in console only. Enhance before V1 launch.

---

## UI Component Library

**shadcn/ui** components are copy-pasted into `src/shared/ui/` (not a package dependency). This means:

- Full control over component code
- No version lock-step with upstream
- Easy to customize Tailwind variants

To add a new component:

```bash
npx shadcn@latest add [component-name]  # runs in frontend/
# e.g. npx shadcn@latest add button
# installs src/components/ui/button.tsx
```

We organize under `src/shared/ui/` to encourage reuse across feature folders.

---

## Environment-Specific Behavior

| Env Var | Effect | Default (unset) |
|---|---|---|
| `NEXT_PUBLIC_ARTEMIS_API_BASE_URL` | Backend API host | `http://127.0.0.1:8000` |
| `NODE_ENV` | Development/production mode | `development` |
| `NEXT_PUBLIC_DISABLE_SSR` | Force client-side rendering (debug) | `false` |

---

## Build & Deploy

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Configure environment variables in Vercel dashboard:
- `NEXT_PUBLIC_ARTEMIS_API_BASE_URL` → your API host (e.g., `https://api.leadengine.example.com`)

### Static Export (Alternative)

Lead Engine is server-rendered (dynamic data), so static export (`next export`) is not suitable. Deploy as Node.js server.

**Dockerfile for frontend:**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["npm", "run", "start"]
```

---

## Accessibility

Basic ARIA labels included. Forms use native `<label>` elements. Table rows have `role="row"`. No full WCAG audit done yet — improve before production use.

---

## Browser Support

Targets modern browsers (Chrome 110+, Firefox 115+, Safari 16+). No IE11 support.

---

## Contributing

See root `README.md` and `LEAD_ENGINE_SPEC.md` for backend guidelines. Frontend should:

1. Match existing component patterns (shadcn/ui + Tailwind utilities)
2. Use TypeScript strictly — no `any` unless absolutely necessary
3. Prefer Server Components when data is read-only
4. Keep client-side state minimal
5. Follow existing page layout: two-column for portal pages, full-width for tables

---

## License

Internal use only — not licensed for public distribution.
