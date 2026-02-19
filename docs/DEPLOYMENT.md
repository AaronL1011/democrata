# Demócrata — Production Deployment

This document covers environment variables, secrets management, and CORS configuration for production deployments.

---

## 1. Environment Variables

### 1.1 Required (Server)

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `DATABASE_URL` | PostgreSQL connection string | See below | Supabase: Settings > Database > Connection pooling (Transaction, port 6543). Local: docker-compose postgres. |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` | Use TLS in production (`rediss://`) when available |
| `QDRANT_URL` | Qdrant vector store URL | `http://qdrant:6333` | Internal URL in Docker; use external URL if Qdrant is hosted |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` | From Supabase dashboard → Settings → API. Same project provides DB + auth. |
| `SUPABASE_ANON_KEY` | Supabase anonymous (public) key | `eyJ...` | Safe to expose to frontend; Row Level Security enforces access |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | `eyJ...` | **Secret.** Server-only; bypasses RLS |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | Required when `EMBEDDING_PROVIDER=openai` or using agent models |
| `STRIPE_SECRET_KEY` | Stripe API secret key | `sk_live_...` | Use `sk_live_` for production |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` | Per-environment; use live webhook secret in production |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `https://app.example.com` | See [§3 CORS](#3-cors) |

### 1.2 Optional (Server)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `EMBEDDING_PROVIDER` | `openai` or `ollama` | `openai` | Use `openai` for production unless self-hosting Ollama |
| `EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` (OpenAI) / `nomic-embed-text` (Ollama) | Must match `EMBEDDING_DIMENSIONS` |
| `EMBEDDING_DIMENSIONS` | Vector dimensionality | `1536` (OpenAI) / `768` (Ollama) | Must match `QDRANT_COLLECTION` vectors |
| `OPENAI_BASE_URL` | Custom OpenAI-compatible API URL | — | For OpenRouter, Azure OpenAI, etc. |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | In Docker: use `http://host.docker.internal:11434` for host Ollama |
| `QDRANT_COLLECTION` | Vector collection name | `democrata_chunks` | Ensure collection exists with correct dimensions |
| `BLOB_STORAGE_PROVIDER` | `local` or `s3` | `local` | Use `s3` for production (see [§2.2 Blob Storage](#22-blob-storage) |
| `BLOB_STORAGE_PATH` | Local blob directory | `./data/blobs` | Only when `BLOB_STORAGE_PROVIDER=local` |
| `S3_BUCKET` | S3 bucket name | `democrata-blobs` | When using S3 |
| `AWS_REGION` | AWS region | `us-east-1` | When using S3 |
| `AWS_ACCESS_KEY_ID` | AWS credentials | — | Optional if using IAM roles / instance profile |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | — | Optional if using IAM roles / instance profile |
| `ANONYMOUS_SESSION_STORE` | `memory` or `redis` | `memory` | Use `redis` for multi-instance or production |
| `API_KEYS` | Comma-separated API keys | — | For programmatic upload/ingestion access |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute per session | `30` | Tune for expected traffic |
| `COST_MARGIN` | Pricing margin (e.g. `0.4` = 40%) | `0.4` | For credit pack pricing display |
| `AGENT_PLANNER_MODEL` | RAG planner model | `gpt-4o-mini` | All `AGENT_*` vars control RAG pipeline |
| `AGENT_EXTRACTOR_MODEL` | RAG extractor model | `gpt-4o` | |
| `AGENT_COMPOSER_MODEL` | RAG composer model | `gpt-4o` | |
| `AGENT_VERIFIER_MODEL` | RAG verifier model | `gpt-4o-mini` | |
| `AGENT_VERIFIER_ENABLED` | Enable verification step | `true` | Set `false` to reduce latency |
| `AGENT_DEFAULT_TOP_K` | Retrieval top-k | `20` | |
| `AGENT_MIN_CHUNKS` | Min chunks for sufficiency | `3` | |
| `JURISDICTION` | Scraper jurisdiction | `au` | For ingestion worker |
| `SCRAPE_CONFIG_DIR` | Path to scrape configs | — | Overrides default config location |
| `SUPABASE_JWT_SECRET` | JWT verification secret | — | Optional; used for token validation |

### 1.3 Build-Time (Frontend)

These are baked into the frontend at **build time** via Vite. Pass as `ARG` in Docker or set in CI:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | API server base URL | `https://api.example.com` |
| `VITE_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | `eyJ...` |

---

## 2. Secrets

### 2.1 Classification

| Secret | Sensitivity | Never commit |
|--------|-------------|--------------|
| `OPENAI_API_KEY` | High | ✓ |
| `SUPABASE_SERVICE_KEY` | High | ✓ |
| `STRIPE_SECRET_KEY` | High | ✓ |
| `STRIPE_WEBHOOK_SECRET` | High | ✓ |
| `DATABASE_URL` | High (contains password) | ✓ |
| `API_KEYS` | High | ✓ |
| `AWS_ACCESS_KEY_ID` | High | ✓ |
| `AWS_SECRET_ACCESS_KEY` | High | ✓ |
| `SUPABASE_JWT_SECRET` | Medium | ✓ |
| `SUPABASE_ANON_KEY` | Low (public by design) | — |
| `REDIS_URL` | Medium (may contain auth) | ✓ if password in URL |
| `VITE_SUPABASE_ANON_KEY` | Low (baked into frontend) | — |

### 2.2 Secret Management

- **Do not** store secrets in `.env` files committed to version control. Use `.env.example` as a template without real values.
- **Production options:**
  - **Docker Compose:** Use [Docker secrets](https://docs.docker.com/engine/swarm/secrets/) or mount secret files.
  - **Kubernetes:** Use [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) or external stores (Vault, AWS Secrets Manager, GCP Secret Manager).
  - **PaaS (Railway, Render, Fly.io, etc.):** Use the platform’s secret/environment variable UI.
- **Rotation:** Plan rotation for `STRIPE_WEBHOOK_SECRET` when changing endpoints; for `API_KEYS` if compromised.

### 2.3 Blob Storage

For production, use S3:

- Set `BLOB_STORAGE_PROVIDER=s3`
- Configure `S3_BUCKET`, `AWS_REGION`
- Prefer IAM roles (ECS task role, EC2 instance profile) over access keys when possible
- Ensure the bucket has appropriate lifecycle and access policies

---

## 3. CORS

### 3.1 How It Works

The API uses FastAPI’s `CORSMiddleware` driven by `CORS_ORIGINS`:

- **`allow_origins`:** Comma-separated list of allowed origins (e.g. `https://app.example.com`)
- **`allow_credentials: true`:** Cookies and `Authorization` headers are sent cross-origin
- **`allow_methods: ["*"]`:** All HTTP methods
- **`allow_headers: ["*"]`:** All headers

Origins are parsed from `CORS_ORIGINS`; empty entries are ignored.

### 3.2 Production Configuration

Set `CORS_ORIGINS` to the **exact** origin(s) of your frontend:

```env
# Single origin
CORS_ORIGINS=https://app.example.com

# Multiple origins (e.g. app + admin subdomain)
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# With port (non-standard)
CORS_ORIGINS=https://app.example.com:4443
```

**Important:**

- Origins must include the scheme (`https://`) and must not have a trailing slash
- `http://localhost:5173` is fine for local development but **must not** appear in production
- If the frontend is served from the same host/port as the API (e.g. via a reverse proxy), ensure the browser’s perceived origin matches what you allow

### 3.3 Security

- **Principle of least privilege:** Only list origins that need API access
- **No wildcards:** Avoid `*` for `allow_origins` when using credentials; browsers will reject it
- **HTTPS:** Use HTTPS origins in production
- **Review regularly:** Update `CORS_ORIGINS` when adding new frontend domains or subdomains

---

## 4. Quick Reference

### Caddy Reverse Proxy (docker-compose)

The stack includes an optional Caddy service for reverse proxy and automatic HTTPS:

- **API_DOMAIN** / **APP_DOMAIN**: Set in `.env` (e.g. `api.example.com`, `app.example.com`)
- Caddy provisions Let's Encrypt certs for real domains; `localhost` uses built-in trust
- Update `VITE_API_URL` and `CORS_ORIGINS` to match your domains

### Minimal Production `.env` Skeleton (Server)

```env
DATABASE_URL=postgresql://postgres.[ref]:[password]@[region].pooler.supabase.com:6543/postgres
REDIS_URL=rediss://redis-host:6379/0
QDRANT_URL=http://qdrant:6333
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=SECRET
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
CORS_ORIGINS=https://app.example.com
BLOB_STORAGE_PROVIDER=s3
S3_BUCKET=democrata-blobs
AWS_REGION=us-east-1
ANONYMOUS_SESSION_STORE=redis
```

### Docker Build Args (Frontend)

```bash
docker build -f frontend/Dockerfile \
  --build-arg VITE_API_URL=https://api.example.com \
  --build-arg VITE_SUPABASE_URL=https://xxx.supabase.co \
  --build-arg VITE_SUPABASE_ANON_KEY=eyJ... \
  -t democrata-frontend ./frontend
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and scaling
- [SCALING.md](SCALING.md) — Horizontal scaling and infrastructure
- [.env.example](../.env.example) — Full variable reference with comments
