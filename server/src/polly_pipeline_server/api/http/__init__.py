from fastapi import APIRouter

from .routes import health, ingestion, rag

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
router.include_router(rag.router, prefix="/rag", tags=["rag"])
