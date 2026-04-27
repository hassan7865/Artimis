# Lead Engine

**Version:** 0.1.0 | **Status:** V1 in progress | **Internal Tool** for an AI agency

A unified lead generation and intelligence platform that automates discovery, enrichment, scoring, and tracking of business opportunities across three domains: agency leads, job market intelligence, and local business outbound prospecting.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Adding a New Source](#adding-a-new-source)
- [Observability](#observability)
- [Troubleshooting](#troubleshooting)
- [Specification & Docs](#specification--docs)

---

## Overview

Lead Engine is a single-user internal tool that runs automated pipelines to surface actionable business opportunities. It operates in three distinct modes over a shared plugin-based architecture:

| Mode | Purpose | Lead Type | Primary Output |
|---|---|---|---|
| `agency_leads` | Identify buying-intent signals for voice AI, automation, and lead-gen services | Businesses/founders expressing need | Scored lead + contact + outreach angle |
| `jobs` | Monitor full-time AI/ML/full-stack job market across boards and company sites | Companies hiring | Scored job + apply priority + company research |
| `outbound` | Build cold-outbound prospect lists from Google Maps by industry + location | Local businesses in target verticals | Contact record + fit score |

### Core Workflow (All Modes)

```
Sources → Dedup → Filter → Enrich → Score → Store → Notify
```

1. **Sources** — Parallel fetching from configured platforms (DuckDuckGo, Reddit, Hacker News, Upwork, Google Maps, job boards)
2. **Deduplication** — Content hash matching prevents duplicates
3. **Filtering** — Location, keywords, freshness before expensive operations
4. **Enrichment** — Contact/company lookup (Hunter.io, Apollo, website scraper, DDG fallback)
5. **Scoring** — LLM-based heuristic scoring (0–100) with reasoning and red flags
6. **Storage** — Persist leads, contacts, runs, costs (SQLite dev / PostgreSQL prod)
7. **Notifications** — Telegram/email alerts for hot leads, digest summaries

---

## Features

### Multi-Mode Operation
- Three distinct operating profiles with separate YAML configurations
- Each mode activates different source combinations and scoring rubrics
- Shared pipeline architecture, different parameters

### Source Plugin System (8+ sources)
| Source | Type | Auth | Location | Modes |
|---|---|---|---|---|
| DuckDuCKGo | Web search | None | Yes | All |
| Reddit | Social | OAuth | Yes | agency, jobs |
| Hacker News | Forum | None | No | agency, jobs |
| Upwork RSS | RSS | None | Yes | agency |
| Google Maps | Maps API | API key | Yes | outbound |
| YC Jobs | Job board | None | Yes | jobs |
| Wellfound | Job board | None | Yes | jobs |
| Glassdoor | Job board | None | Yes | jobs |

**Extensibility:** Adding a new source = 1 file + 1 enum entry + 1 registry line. Zero changes to orchestration logic.

### LLM-Powered Scoring
- Structured output via Pydantic schemas (OpenAI/Anthropic JSON mode)
- Configurable prompts per mode (YAML-driven)
- Batch processing (default 8 leads/call) for token efficiency
- Scoring dimensions: `buying_intent`, `fit`, `urgency`, `budget_signal`, `seniority`, `recommended_channel`
- Full audit trail: raw LLM output, token counts, cost per call tracked

### Cost & Rate Management
- Per-run LLM spend cap (e.g., $2/run)
- Daily LLM budget cap (e.g., $20/day)
- Per-source rate limits enforced via semaphores
- Circuit breaker: 3 consecutive failures → skip for next run
- Budget exceeded → abort run + immediate notification

### Contact Enrichment Pipeline
Multi-provider chaining with caching:
1. Website scraper (selectolax HTML parsing)
2. Hunter.io API (domain email hunting)
3. Apollo.io API (contact database)
4. DuckDuckGo fallback (free-form search)

Enrichment cached by domain to avoid redundant API spend.

### Notification System
- **Telegram bot** — instant hot lead alerts (score ≥ threshold)
- **SMTP email** — daily digest, run summaries
- **Webhooks** — outgoing integrations (future)
- Non-fatal: notifier failures never abort a run

### Run Tracking & Analytics
- `RunRecord` with per-source stats (fetched, deduped, filtered, enriched, scored, persisted, errors)
- LLM token counts and USD cost per run
- Error aggregation and circuit breaker state
- Full run history with timing breakdowns

### Dashboard (Next.js Frontend)
- **Overview** — aggregated stats across modes
- **Lead Browser** — filterable table (mode, score, source, status, date), inline status updates
- **Lead Detail** — raw content, enrichment data, score reasoning, contact info, status timeline
- **Run History** — per-mode runs with cost, timing, source breakdown
- **Run Detail** — per-source stats, error logs, LLM spend
- **Mode Configs** — YAML editor with schema validation + manual run trigger
- **Source Catalog** — health status, rate limits, last success timestamp
- **Settings** — API key management (stored in database)

---

## Architecture

### High-Level Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       FRONTEND (Next.js)                     │
│  Dashboard │ Lead browser │ Mode configs │ Run history       │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP REST (FastAPI)
┌──────────────────────────────▼───────────────────────────────┐
│                      BACKEND API (FastAPI)                   │
│   /leads │ /runs │ /sources │ /modes │ /enrich │ /export     │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                         ORCHESTRATOR                         │
│  modes/run_engine.py: execute_run() pipeline                 │
└──┬──────────┬──────────┬──────────┬──────────┬──────────┬───┘
   │          │          │          │          │          │
┌──▼──┐  ┌────▼────┐  ┌──▼──────┐ ┌─▼─────┐  ┌─▼───────┐ ┌▼──────┐
│Sources│ │Filters │ │Enricher │ │Scorer │  │Storage  │ │Notifier│
│(plugin│ │(chain) │ │(plugin) │ │(LLM)  │  │(SQLite) │ │(plugin)│
│system)│ └────────┘ └─────────┘ └───────┘  └─────────┘ └────────┘
└───────┘
```

### Design Patterns

**Repository Pattern** — Storage layer (`storage/repository.py`) implements `Storage` ABC. Complete boundary: no ORM models leak outside.

**Plugin Architecture** — Sources, enrichers, notifiers all defined by interfaces. New implementations require only new files. Open/Closed principle strictly enforced.

**Dependency Injection** — `api/deps.py` provides `get_storage`, `get_settings`. Composition root is `create_app()`.

**Clean/Hexagonal Architecture** — Core domain (`core/`) has zero I/O dependencies. Adapters (API, DB, HTTP clients) depend inward.

**Strategy Pattern** — Enrichment pipeline, notification channels, scoring backends all swappable via interface.

**Factory Pattern** — `sources/factory.py` builds real vs mock clients based on configuration/credentials.

### Data Models (Pydantic → SQLAlchemy)

- `RawLead` — Unstructured output from a source
- `Lead` — Enriched, scored, persisted entity
- `EnrichmentResult` — Company + contacts data
- `ScoreResult` — LLM output with reasoning
- `Contact` — Individual person record with confidence score
- `RunRecord` — Execution metadata, timing, costs
- `SourceRunStat` — Per-source metrics within a run

### Extensibility Guarantee

Adding a new source (e.g., "Indie Hackers") requires exactly:

1. `sources/indie_hackers.py` implementing `Source` ABC
2. Enum entry in `constants.SourceName`
3. Registry entry in `sources/__init__.py`
4. Config snippet in the relevant `modes/*.yaml`

**Zero changes** to orchestrator, storage, scoring, or any other module. If a PR modifying existing files is needed, the abstraction leaked.

---

## Technology Stack

### Backend
- **Language:** Python 3.11
- **API:** FastAPI (async) + Uvicorn
- **ORM:** SQLAlchemy 2.0 (async) with Alembic migrations
- **Validation:** Pydantic v2 + pydantic-settings
- **HTTP Client:** httpx (async-native)
- **Resilience:** tenacity (retry + exponential backoff)
- **Scheduling:** APScheduler (in-process, V1)
- **LLM:** Azure OpenAI (primary), OpenAI, Anthropic (via `LLMClient` interface)
- **Parsing:** selectolax (fast HTML), ddgs (DuckDuckGo search)
- **Logging:** structlog (structured JSON)

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript + React 19
- **Styling:** Tailwind CSS v4 + shadcn/ui components
- **Data Fetching:** Native fetch (server components) + client-side mutations

### Infrastructure
- **Package Manager:** uv (Python), npm (Node)
- **Linting/Format:** ruff, mypy --strict
- **Testing:** pytest, pytest-asyncio, pytest-mock, vcrpy
- **Containerization:** Docker Compose (PostgreSQL)
- **Database:** SQLite (dev/test), PostgreSQL 16 (prod)

---

## Project Structure

```
/Users/mac/Artimis/
├── pyproject.toml              # Dependencies, tool config (ruff, mypy, pytest)
├── uv.lock                     # Locked dependency tree
├── .env.example                # Environment template
├── README.md                   # This file
├── LEAD_ENGINE_SPEC.md         # Full product spec (653 lines)
├── BACKEND_CODEBASE.md         # Backend handoff guide
├── FRONTEND_CODEBASE.md        # Frontend handoff guide
├── docker-compose.yml          # Postgres service
├── alembic.ini                 # Migration config
│
├── src/lead_engine/            # Backend package
│   ├── __init__.py
│   │
│   ├── api/                   # FastAPI application
│   │   ├── main.py            # App factory, CORS, health
│   │   ├── deps.py            # Dependency injection
│   │   ├── routers/
│   │   │   ├── leads.py       # CRUD + filtering
│   │   │   ├── runs.py        # Run execution + listing
│   │   │   ├── sources.py     # Source catalog
│   │   │   ├── modes.py       # Mode config CRUD
│   │   │   └── enrichment.py  # Manual enrichment trigger
│   │   └── schemas/           # Pydantic request/response models
│   │
│   ├── core/                  # Pure business logic (no I/O)
│   │   ├── models.py          # Domain models (RawLead, Lead, etc.)
│   │   ├── interfaces.py      # ABCs: Source, Enricher, Scorer, Notifier, Storage, LLMClient
│   │   ├── errors.py          # Exception hierarchy
│   │   ├── filters.py         # Location, keyword, dedup, score threshold filters
│   │   └── dedup.py           # Content hash functions
│   │
│   ├── sources/               # Platform integrations (plugin system)
│   │   ├── duckduckgo.py
│   │   ├── reddit.py
│   │   ├── hackernews.py
│   │   ├── upwork_rss.py
│   │   ├── google_maps.py
│   │   ├── job_search_sources.py  # YC, Wellfound, Glassdoor
│   │   ├── mock_sources.py        # Fallback when API keys missing
│   │   ├── registry.py       # SOURCE_REGISTRY + mode→source mappings
│   │   └── factory.py        # Builds source instances (real vs mock)
│   │
│   ├── modes/
│   │   └── run_engine.py     # Orchestrator: execute_run() pipeline
│   │
│   ├── storage/              # Database layer
│   │   ├── orm.py            # SQLAlchemy table models
│   │   ├── db.py             # Engine + async sessionmaker
│   │   └── repository.py     # SqlaRepository implementing Storage ABC
│   │
│   ├── llm/                  # LLM integrations
│   │   ├── azure_openai_client.py  # AzureOpenAI (LLMClient)
│   │   ├── anthropic_client.py     # Alternative Anthropic client
│   │   ├── cost_tracker.py         # Per-run budget enforcement
│   │   └── pricing.py              # Token→USD conversion tables
│   │
│   ├── enrichment/           # Contact enrichment (scaffolded, V2)
│   │   └── __init__.py
│   │
│   ├── notifiers/            # Notification channels (scaffolded, V2)
│   │   └── __init__.py
│   │
│   ├── scheduler/            # APScheduler integration (scaffolded, V2)
│   │   └── __init__.py
│   │
│   ├── constants.py          # Enums: ModeName, SourceName, ScoreDimension, etc.
│   ├── settings.py           # pydantic-settings (env loading, secrets)
│   └── logging_setup.py      # structlog configuration
│
├── alembic/                  # Migration scripts
│   └── versions/
│       └── 5c4c247b132d_initial_schema.py
│
├── tests/
│   ├── unit/
│   │   ├── core/             # models, interfaces, filters, dedup
│   │   ├── sources/          # source factory + contract tests
│   │   ├── llm/              # cost tracker, pricing, client
│   │   ├── storage/          # repository tests
│   │   └── api/              # router unit tests
│   ├── integration/
│   │   └── test_execute_run_api.py  # Full pipeline with mocked sources
│   ├── fixtures/             # VCR cassettes, sample data (empty in repo)
│   └── conftest.py           # pytest fixtures (repo, engine, session)
│
├── frontend/                 # Next.js application
│   ├── package.json          # Next.js 16, React 19, Tailwind v4
│   ├── postcss.config.mjs
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── page.tsx                      # Overview dashboard
│   │   │   ├── agent/page.tsx                # Generic runner
│   │   │   ├── job-finder/page.tsx           # Jobs portal
│   │   │   ├── outbound/page.tsx             # Outbound portal
│   │   │   ├── leads/                        # Lead listing + detail
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   ├── runs/                         # Run history + detail
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   ├── sources/page.tsx              # Source catalog
│   │   │   ├── modes/                        # Mode management
│   │   │   │   ├── page.tsx
│   │   │   │   └── [name]/page.tsx
│   │   │   └── settings/page.tsx             # API key management
│   │   │
│   │   ├── shared/
│   │   │   ├── lib/api.ts        # Type-safe API client
│   │   │   └── ui/
│   │   │       ├── app-shell.tsx     # Navigation
│   │   │       └── run-agent-form.tsx # Reusable execution form
│   │   └── globals.css
│   └── README.md
│
└── scripts/                  # CLI utilities (placeholder)
    ├── run_mode.py           # Trigger a mode from CLI
    ├── init_db.py
    └── seed_demo_data.py
```

---

## Quick Start

The fastest path to running Lead Engine locally:

```bash
# 1. Prerequisites (see full list below)
#    - Python 3.11
#    - Node.js 20+
#    - uv (Python package manager)
#    - Docker (for Postgres)

# 2. Clone & install dependencies
git clone <your-repo-url>
cd lead-engine
uv sync --all-extras
cd frontend && npm install && cd ..

# 3. Start PostgreSQL
docker compose up -d postgres  # listens on host port 5433

# 4. Configure environment
cp .env.example .env
# Edit .env if needed; defaults work with docker-compose

# 5. Run database migrations
uv run alembic upgrade head

# 6. Start backend API (http://127.0.0.1:8000)
uv run uvicorn lead_engine.api.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start frontend (new terminal)
cd frontend
npm run dev  # http://127.0.0.1:3000
```

Visit `http://127.0.0.1:3000` to access the dashboard.

---

## Configuration

### Environment Variables (`.env`)

Backend variables (see `.env.example`):

```env
# Database
LEAD_ENGINE_DATABASE_URL=postgresql+asyncpg://lead_engine:lead_engine@localhost:5433/lead_engine

# LLM Provider (choose one)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Alternative providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# External APIs (optional but recommended)
SERPER_API_KEY=your_serper_key  # Google Maps via Serper
HUNTER_API_KEY=your_hunter_key  # Email enrichment
APOLLO_API_KEY=your_apollo_key  # Contact enrichment

# Notifications
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=your_chat_id
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Scheduler (V2)
LEAD_ENGINE_SCHEDULER_ENABLED=true

# Costs (USD)
LEAD_ENGINE_MAX_LLM_COST_PER_RUN=2.00
LEAD_ENGINE_MAX_LLM_COST_PER_DAY=20.00
```

Frontend environment (optional, `frontend/.env.local`):

```env
NEXT_PUBLIC_ARTEMIS_API_BASE_URL=http://127.0.0.1:8000
```

### Mode Configuration (YAML)

Mode files live in `src/lead_engine/modes/` (currently stubbed; create based on `modes/agency_leads.yaml` template from spec):

```yaml
name: agency_leads
description: "Find buying-intent signals for AI agency services."

# Activate these sources for this mode
sources:
  - name: duckduckgo
    queries:
      - 'site:twitter.com "looking for" "voice AI"'
      - '"just raised" "seed" "looking for" "AI automation"'
    max_results_per_query: 20
  - name: reddit
    subreddits: [Entrepreneur, SaaS, smallbusiness]
    keywords: ["voice AI", "AI agent", "automate"]
    lookback_hours: 24

# Cheap pre-scoring filters
filters:
  locations:
    include_countries: [US, CA, GB, AU]
    include_remote: true
  exclude_keywords: ["student project", "free", "pro bono"]
  min_content_length: 50
  max_age_hours: 72

# Enrichment pipeline
enrichment:
  enabled: true
  providers: [website_scraper, hunter, ddg_fallback]
  only_if_score_above: 70  # skip low-score leads

# LLM scoring configuration
scoring:
  prompt_path: "scoring/prompts/agency_leads.md"
  hot_threshold: 85        # immediate notification
  save_threshold: 60       # minimum to persist
  batch_size: 8            # leads per LLM call

# Notification rules
notifications:
  - channel: telegram
    min_score: 85
    include_enrichment: true
  - channel: email
    digest_time: "08:00"

# Scheduling (V2)
schedule:
  cron: "0 */3 * * *"  # every 3 hours
  enabled: false        # manual only for V1

# Budgets
budgets:
  max_llm_cost_usd_per_run: 2.00
  max_enrichment_calls_per_run: 50
```

Create similar files for `jobs.yaml` and `outbound.yaml`. The backend auto-discovers them.

---

## Development

### Directory Conventions

- All new source files go in `src/lead_engine/sources/`
- Core logic in `src/lead_engine/core/` — must be pure, no side effects
- Database models in `src/lead_engine/storage/` — only ORM layer touches SQLAlchemy
- API layer in `src/lead_engine/api/` — FastAPI routers + schemas
- Frontend pages in `src/app/` per Next.js App Router conventions

### Code Quality Standards

```bash
# From repo root

# Linting (ruff replaces black/flake8/isort)
uv run ruff check src tests

# Auto-fix
uv run ruff check src tests --fix

# Type checking (strict mode on core/)
uv run mypy src/lead_engine/core

# Full type check (some deps untyped)
uv run mypy src/lead_engine

# Format check (ruff format is opinionated)
uv run ruff format src tests --check
```

**CI Expectations:**
- `ruff check` — zero errors (allowed TC001 in type-checking blocks)
- `mypy --strict` on `core/` — zero errors
- `pytest` — all tests passing, ≥80% coverage on `core/`

### IDE Setup

**VS Code recommended settings** (`.vscode/settings.json`):

```json
{
  "python.analysis.typeCheckingMode": "strict",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "mypy-type-checker.args": ["--strict"]
}
```

Install the official Ruff extension for instant feedback.

### Adding a New Source (The Primary Extension Task)

See [Adding a New Source](#adding-a-new-source) section below for the complete protocol.

---

## Testing

### Test Layout

```
tests/
├── unit/
│   ├── core/               # Pure logic (filters, models, dedup)
│   ├── sources/            # Source contract tests + mocks
│   ├── llm/                # Cost tracker, pricing, clients
│   ├── storage/            # Repository
│   └── api/                # Router validation
├── integration/
│   ├── test_execute_run_api.py   # Full orchestrator with mocked sources
│   └── test_full_pipeline.py     # End-to-end with real DB (optional)
└── fixtures/               # VCR cassettes, recorded HTTP fixtures (blank in repo)
```

### Running Tests

```bash
# All tests (fast: ~5s)
uv run pytest -q

# Verbose
uv run pytest -v

# With coverage
uv run pytest --cov=src/lead_engine --cov-report=html
open htmlcov/index.html

# Specific test file
uv run pytest tests/unit/sources/test_duckduckgo.py -v

# Integration only
uv run pytest tests/integration/ -v

# Lint + typecheck + test (pre-commit style)
uv run ruff check src tests && uv run mypy src/lead_engine/core && uv run pytest -q
```

### Contract Testing (VCR Pattern)

Sources that hit external APIs should use `vcrpy` to record HTTP interactions:

```python
import vcr

@vcr.use_cassette("tests/fixtures/duckduckgo/search.yaml")
async def test_duckduckgo_search():
    source = DuckDuckGoSource(config={"max_results": 5})
    leads = await source.fetch(SourceQuery(query="voice AI"))
    assert len(leads) > 0
```

Record new fixtures with:

```bash
# Delete old cassette, run test once with network, it re-records
rm tests/fixtures/duckduckgo/search.yaml
uv run pytest tests/unit/sources/test_duckduckgo.py::test_search -v
```

Commit recorded fixtures with the source code.

---

## Deployment

### Development (Local)

Already covered in [Quick Start](#quick-start). SQLite is the default for local runs:

```env
LEAD_ENGINE_DATABASE_URL=sqlite+aiosqlite:///lead_engine.db
```

No Docker needed for dev. Postgres is only for production parity.

### Production (VPS)

**Target:** Single-user VPS (Hetzner, Railway, Fly.io — $5–10/mo)

1. **Provision server** (Ubuntu 24.04 recommended)
2. **Install system deps:** Python 3.11, Node.js 20, uv, PostgreSQL 16
3. **Clone repo + install:**
   ```bash
   git clone <repo>
   cd lead-engine
   uv sync --all-extras
   cd frontend && npm ci --only=production && cd ..
   ```
4. **Production env:** Copy `.env.example` → `.env` on server; fill in real API keys.
5. **Database:**
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE lead_engine;"
   sudo -u postgres psql -c "CREATE USER lead_engine WITH PASSWORD '<strong_password>';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lead_engine TO lead_engine;"
   uv run alembic upgrade head
   ```
6. **Build frontend:**
   ```bash
   cd frontend
   npm run build  # creates .next/ (standalone if configured)
   ```
7. **Process manager:** Use `systemd` or `supervisord` to run:
   ```bash
   # Backend API
   uvicorn lead_engine.api.main:app --host 0.0.0.0 --port 8000
   ```
8. **Reverse proxy:** Nginx/Caddy → 8000 (API) + 3000 (frontend, or build static and serve via nginx)
9. **Backups:** SQLite → nightly `litestream` or `cron` + `gcloud`/`s3`. Postgres → `pg_dump`.

### Docker (Alternative)

There is a `docker-compose.yml` for Postgres only. Full containerization (backend + frontend + DB) is TODO:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports: ["5433:5432"]
    environment:
      POSTGRES_DB: lead_engine
      POSTGRES_USER: lead_engine
      POSTGRES_PASSWORD: lead_engine

  backend:
    build: .
    command: uvicorn lead_engine.api.main:app --host 0.0.0.0 --port 8000
    env_file: .env
    depends_on: [postgres]

  frontend:
    build:
      context: ./frontend
      target: production
    ports: ["3000:3000"]
    depends_on: [backend]
```

---

## Adding a New Source

This is the primary extension mechanism. The codebase is designed so adding a new platform (e.g., Indie Hackers, Product Hunt, Twitter) requires **zero modifications** to existing source files.

### Step-by-Step

**1. Create the source file** — `src/lead_engine/sources/my_new_source.py`

```python
from typing import AsyncIterator
from ...core.interfaces import Source
from ...core.models import RawLead, SourceQuery
from .base import HTTPSourceBase  # optional helper class

class MyNewSource(Source):
    """Integrates with MyNewSource platform."""

    name = "my_new_source"                     # unique key
    rate_limit_per_hour = 1000                 # for semaphore enforcement
    supports_location = True                   # can filter by geo?
    requires_auth = True                       # needs API key?

    def __init__(self, config: dict):
        super().__init__(config)
        # initialize client (httpx, SDK, etc.)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("api_key required")

    def validate_config(self, config: dict) -> None:
        """Raise if required keys missing."""
        if "api_key" not in config:
            raise ValueError("config must contain 'api_key'")

    async def fetch(self, query: SourceQuery) -> list[RawLead]:
        """
        Query parameters come from the mode YAML for this source.
        Returns list of RawLead objects (raw, un-enriched, un-scored).
        """
        # 1. Query the platform
        # 2. Parse each result into RawLead(content=..., source_url=..., ...)
        # 3. Return list
        results = await self._search(query.query, query.location)
        return [
            RawLead(
                source_name=self.name,
                source_url=item.url,
                content=item.text,
                title=item.title,
                author=item.author,
                posted_at=item.date,
                location_hint=query.location.raw if query.location else None,
                raw_metadata=item.extra,
            )
            for item in results
        ]

    async def _search(self, query: str, location) -> list[Item]:
        # actual HTTP calls here (httpx, retry, error handling)
        pass
```

**2. Register the source** — `src/lead_engine/sources/__init__.py`

```python
from .registry import register_source
from .my_new_source import MyNewSource

register_source("my_new_source", MyNewSource)
```

**3. Add enum entry** — `src/lead_engine/constants.py`

```python
class SourceName(str, Enum):
    # ... existing entries ...
    MY_NEW_SOURCE = "my_new_source"
```

**4. Map to modes** — `src/lead_engine/sources/registry.py`

Add `MyNewSource` to the appropriate `MODE_TO_SOURCES` lists:

```python
MODE_TO_SOURCES = {
    ModeName.AGENCY_LEADS: [
        SourceName.DUCKDUCKGO,
        SourceName.REDDIT,
        SourceName.MY_NEW_SOURCE,  # ← your source
    ],
    # ...
}
```

**5. Add mode YAML snippet** — `src/lead_engine/modes/agency_leads.yaml`

```yaml
sources:
  - name: my_new_source
    api_key: ${MY_NEW_SOURCE_API_KEY}  # from env
    queries:
      - "voice AI pricing"
      - "automation services"
    max_results_per_query: 15
```

**6. Write contract test** — `tests/unit/sources/test_my_new_source.py`

```python
import pytest
from lead_engine.sources.my_new_source import MyNewSource

@pytest.mark.asyncio
async def test_fetch_returns_raw_leads():
    source = MyNewSource(config={"api_key": "test"})
    query = SourceQuery(query="test", location=None)
    leads = await source.fetch(query)
    assert isinstance(leads, list)
    assert all(isinstance(l, RawLead) for l in leads)
```

Record HTTP fixtures with VCR for deterministic tests.

**7. Done.** No other files touched. Run `pytest` to verify.

### Source Implementation Checklist

- [ ] Subclass `Source` ABC
- [ ] Set class vars: `name`, `rate_limit_per_hour`, `supports_location`, `requires_auth`
- [ ] Implement `validate_config(config)` — raise on missing required keys
- [ ] Implement `async fetch(query: SourceQuery) -> list[RawLead]`
- [ ] Parse results into `RawLead` with proper `source_name`, `source_url`, `content`
- [ ] Handle pagination (if needed) within the `max_results` constraint
- [ ] Implement retry + exponential backoff for network calls
- [ ] Redact API keys from logs (use `structlog`'s redaction processor)
- [ ] Raise `SourceFetchError` on unrecoverable failures (caught by orchestrator)
- [ ] Unit test + contract test (VCR cassette)
- [ ] Update `constants.py` + `registry.py` + mode YAML

---

## Observability

### Structured Logging

All logs are JSON in production, colorized in development. Every log line includes:

```json
{
  "timestamp": "2026-04-26T04:26:19.123Z",
  "level": "info",
  "event": "source_fetch_complete",
  "source": "duckduckgo",
  "mode": "agency_leads",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "fetched": 42,
  "duration_ms": 1250
}
```

Secrets are automatically redacted (keys matching `*_KEY`, `*_TOKEN`, `*_SECRET`, `*_PASSWORD`).

Set log level via env:

```bash
LEAD_ENGINE_LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","timestamp":"2026-04-26T04:26:19Z","service":"lead-engine"}
```

Future: `/metrics` endpoint with Prometheus-format counters.

### Database Inspection

```bash
# Open SQLite CLI (dev)
sqlite3 lead_engine.db

# View recent leads
SELECT id, mode, source_name, status, score FROM leads ORDER BY created_at DESC LIMIT 10;

# View run history
SELECT id, mode, status, start_time, end_time, llm_cost_usd FROM runs ORDER BY start_time DESC LIMIT 5;
```

PostgreSQL: same queries via `psql`.

Run migrations:

```bash
uv run alembic current  # show current revision
uv run alembic history  # list all migrations
uv run alembic upgrade head  # apply pending
uv run alembic downgrade -1  # rollback one (dev only)
```

---

## Troubleshooting

### Backend won't start — database connection error

**Symptom:** `asyncpg.exceptions.InvalidPasswordError` or timeout.

**Fix:**
1. Ensure Postgres is running: `docker compose ps`
2. Verify `LEAD_ENGINE_DATABASE_URL` in `.env` matches docker-compose credentials (`lead_engine:lead_engine@localhost:5433`)
3. For local SQLite dev, change to:
   ```env
   LEAD_ENGINE_DATABASE_URL=sqlite+aiosqlite:///./lead_engine.db
   ```
4. Remove existing DB file (if SQLite) and re-run migrations.

### Frontend shows "Failed to fetch" on run trigger

**Cause:** API base URL incorrect or CORS blocked.

**Fix:**
1. Frontend `.env.local` must have correct `NEXT_PUBLIC_ARTEMIS_API_BASE_URL`
2. Backend `api/main.py` has CORS allowlist. Add your dev origin if needed:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
   )
   ```
3. Backend must be running on port 8000.

### No leads appear after a run

**Diagnose:**

```bash
# 1. Check run status in DB
uv run python -c "from lead_engine.storage.db import get_session; from lead_engine.storage.orm import RunRow; import asyncio; asyncio.run(lambda: next(get_session()).query(RunRow).all())"

# 2. Look at run detail in UI → /runs/[id] for per-source errors
# 3. Check backend logs for "SourceFetchError" or "rate limit" messages
# 4. Verify source config in mode YAML (queries, subreddits, etc.)
# 5. Ensure API keys for paid sources are set (HUNTER_API_KEY, SERPER_API_KEY)
```

### LLM costs ballooning

**Likely causes:**
- `batch_size` too small (1 lead/call) → increase to 8
- `save_threshold` too low (everything gets scored) → raise to 70+
- Duplicate leads slipping through dedup → check `seen_hashes` table

**Mitigations:**
```env
LEAD_ENGINE_MAX_LLM_COST_PER_RUN=2.00
LEAD_ENGINE_MAX_LLM_COST_PER_DAY=20.00
```

Orchestrator aborts run when caps hit.

### Source rate-limited (429)

Orchestrator respects `rate_limit_per_hour` via semaphore. If a source still hits limits:
1. Increase `rate_limit_per_hour` in source class (if platform allows higher)
2. Reduce concurrent fetching in orchestrator (serial vs parallel)
3. Add exponential backoff in source implementation (tenacity already used in base classes)

### Tests fail intermittently (network fixtures)

VCR cassettes may be corrupted or missing. Regenerate:

```bash
rm -rf tests/fixtures
uv run pytest --record-mode=once  # re-record all fixtures
```

For time-sensitive tests, use `freezegun` to freeze `datetime.utcnow()`.

### PostgreSQL migration fails

Alembic revision mismatch. Options:

```bash
# Start fresh (dev only)
uv run alembic downgrade base
uv run alembic upgrade head

# Force re-create (WARNING: data loss)
rm -rf alembic/versions/*
uv run alembic revision --autogenerate -m "reinitialise"
uv run alembic upgrade head
```

If production, write a proper migration instead of resetting.

---

## Specification & Docs

- **`LEAD_ENGINE_SPEC.md`** — Full product specification (653 lines), build order, acceptance criteria
- **`BACKEND_CODEBASE.md`** — Backend handoff guide: entry points, data flow, current gaps
- **`FRONTEND_CODEBASE.md`** — Frontend structure, routes, API client, component patterns
- **`pyproject.toml`** — Dependency declarations, tool configuration (ruff, mypy, pytest)

### Architecture Deep Dives

Key files to understand the system:

- `src/lead_engine/core/interfaces.py` — The contract for all plugins (read first)
- `src/lead_engine/modes/run_engine.py` — Orchestrator pipeline (fetch → dedup → filter → enrich → score → store → notify)
- `src/lead_engine/storage/repository.py` — Repository pattern implementation, dedup ledger, enrichment cache
- `src/lead_engine/sources/registry.py` — Source metadata and mode mappings
- `frontend/src/shared/lib/api.ts` — Type-safe API client consumed by all pages

---

## Contributing

This is a single-developer internal tool. No external contributions accepted at this time. However, if you're the maintainer:

1. Create a feature branch from `main`
2. Follow the coding principles in `LEAD_ENGINE_SPEC.md` (SRP, clean architecture, type safety)
3. Write tests first (TDD encouraged)
4. Ensure `pytest`, `ruff check`, and `mypy` all pass
5. Open a PR with a clear description linking to the YAML mode config changes
6. Update this README and `BACKEND_CODEBASE.md`/`FRONTEND_CODEBASE.md` as needed

### Commit Message Convention

Conventional commits:

```
feat: add Reddit source with subreddit filtering
fix: handle empty enrichment results gracefully
refactor: extract dedup logic into pure function
test: add VCR cassette for DuckDuckGo source
docs: update README with deployment steps
```

---

## License

Internal use only — not licensed for public distribution. All rights reserved.

---

**Last updated:** 2026-04-26 | **Implements V1 specification** (in progress)
