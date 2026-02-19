import os

import asyncpg
import httpx
import redis.asyncio as redis
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333").rstrip("/")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://democrata:democrata_dev@localhost:5432/democrata",
)
HEALTH_TIMEOUT = 2.0


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
    checks: dict[str, str] = {}
    all_ok = True

    try:
        client = redis.from_url(REDIS_URL)
        await client.ping()
        await client.aclose()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = str(e)
        all_ok = False

    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT) as client:
            response = await client.get(f"{QDRANT_URL}/healthz")
            if response.status_code == 200:
                checks["qdrant"] = "ok"
            else:
                checks["qdrant"] = f"status {response.status_code}"
                all_ok = False
    except Exception as e:
        checks["qdrant"] = str(e)
        all_ok = False

    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=HEALTH_TIMEOUT)
        await conn.close()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = str(e)
        all_ok = False

    status_code = 200 if all_ok else 503
    body = {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
    return JSONResponse(content=body, status_code=status_code)
