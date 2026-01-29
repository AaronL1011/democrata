.PHONY: install server frontend dev test lint clean

# Install all dependencies (Python with uv, frontend with pnpm)
install:
	cd server && uv sync --extra dev
	pnpm install

# Run the API server (FastAPI)
server:
	cd server && uv run uvicorn polly_pipeline_server.main:app --reload

# Run the frontend dev server (Svelte + Vite)
frontend:
	pnpm --filter frontend dev

# Run server and frontend in parallel (use -j2)
dev: server frontend

# Run tests
test:
	cd server && uv run pytest

# Lint
lint:
	cd server && uv run ruff check src
	cd server && uv run ruff format --check src

# Fix lint (format + auto-fix)
lint-fix:
	cd server && uv run ruff check src --fix
	cd server && uv run ruff format src

# Remove generated/cached artifacts
clean:
	rm -rf server/.venv
	rm -rf node_modules frontend/node_modules
	rm -rf frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
