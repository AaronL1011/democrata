# Demócrata

Demócrata is a political, social and government data ingestion engine that provides file-based RAG with a non-partisan, simple and accessible research portal.

<img width="3500" height="1951" alt="image" src="https://github.com/user-attachments/assets/374cfd82-ed39-4a24-8c83-578e2fb373a2" />
<img width="3500" height="1951" alt="image" src="https://github.com/user-attachments/assets/74d799b3-b5b7-4e96-89fd-fcad3642ee3b" />

---

See [SPEC.md](SPEC.md) for the full spec.

**Documentation:** [SPEC.md](SPEC.md) (product spec) · [docs/](docs/) — [Architecture](docs/ARCHITECTURE.md), [Schemas](docs/SCHEMAS.md), [Data models](docs/DATA_MODELS.md), [Implementation](docs/IMPLEMENTATION.md), [Cost model](docs/COST_MODEL.md)

## Prerequisites

- **Python 3.12+** and [uv](https://docs.astral.sh/uv/)
- **Node.js** and [pnpm](https://pnpm.io/) (e.g. `corepack enable && corepack prepare pnpm@latest --activate`)

## Monorepo layout

- `server/` — Python FastAPI + gRPC app (uv, `pyproject.toml`)
- `frontend/` — Svelte + Vite app (pnpm workspace)

## Quick start

```bash
make install    # uv sync (server) + pnpm install (frontend)
make server     # Run API server (http://127.0.0.1:8000)
make frontend   # Run frontend dev server (separate terminal)
make test       # Run server tests
make lint       # Lint server (ruff)
```

## Makefile targets

| Target      | Description                    |
|------------|--------------------------------|
| `install`  | Install server + frontend deps |
| `server`   | Run FastAPI server             |
| `frontend` | Run Svelte dev server          |
| `dev`      | Run server and frontend (-j2)  |
| `test`     | Run server tests               |
| `lint`     | Ruff check + format check      |
| `lint-fix` | Ruff fix + format              |
| `clean`    | Remove .venv, node_modules, dist |
