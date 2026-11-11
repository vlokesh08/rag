# RAG Knowledge Assistant

A full-stack knowledge assistant: authenticated users create knowledge bases,
chat with an LLM, and (from Phase 2 onward) ground answers in their own
uploaded documents with citations. This repository currently implements
**Phase 1 — Foundation** only. See `docs/RAG_IMPLEMENTATION_SPEC.md` for the
full product specification and phase plan.

## Stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui,
  TanStack Query, React Hook Form + Zod.
- **Backend**: FastAPI, SQLAlchemy 2.x (async), Alembic, PostgreSQL + pgvector.
- **Background jobs**: ARQ (Redis-backed).
- **LLM provider**: Anthropic (Claude), behind a swappable provider interface.
- **Auth**: email + password, server-side (DB-backed) sessions via an
  HTTP-only cookie.

## Prerequisites

- Docker and Docker Compose
- An Anthropic API key (for live chat generation)

## Setup

1. Copy the environment file and fill in your Anthropic API key:

   ```bash
   cp .env.example .env
   # edit .env and set ANTHROPIC_API_KEY
   ```

2. Start the full stack (Postgres + pgvector, Redis, migrations, backend API,
   worker, frontend):

   ```bash
   docker compose up -d --build
   ```

   The `migrate` service runs `alembic upgrade head` once and exits; `backend`
   and `worker` wait for it to complete successfully before starting.

3. Open the app:

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health checks: http://localhost:8000/api/v1/health/live and `/ready`

## Local development without Docker

**Backend** (requires `uv`, Python 3.12, and a running Postgres + Redis — the
`backend/.env` file points these at `localhost` instead of the compose
service names):

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
# in a separate terminal, for background jobs:
uv run arq app.workers.worker_settings.WorkerSettings
```

**Frontend** (requires `pnpm`):

```bash
cd frontend
pnpm install
pnpm dev
```

## Tests

**Backend** (runs against an in-memory SQLite DB and a fake LLM provider — no
real API key or running Postgres/Redis needed):

```bash
cd backend
uv run pytest
uv run ruff check .
uv run mypy app
```

**Frontend**:

```bash
cd frontend
pnpm test
pnpm lint
pnpm exec tsc --noEmit
```

## Repository layout

```
backend/    FastAPI app, SQLAlchemy models, Alembic migrations, ARQ worker, tests
frontend/   Next.js app (App Router), components, hooks, services
docs/       Product and implementation specification
```

## Scope

This repository currently implements Phase 1 (Foundation) from
`docs/RAG_IMPLEMENTATION_SPEC.md`: authentication, knowledge-base CRUD,
conversations/messages, and basic (non-RAG) LLM chat over SSE. Document
ingestion, retrieval, citations, evaluation, and memory are later phases and
are intentionally not implemented yet.
