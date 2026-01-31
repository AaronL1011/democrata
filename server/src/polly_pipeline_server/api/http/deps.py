import hashlib
import os
from functools import lru_cache

from fastapi import Request

from polly_pipeline_server.adapters.cache.redis import RedisCache
from polly_pipeline_server.adapters.extraction import ContentTypeExtractor
from polly_pipeline_server.adapters.llm.factory import (
    Embedder,
    LLMClient,
    create_embedder,
    create_llm_client,
)
from polly_pipeline_server.adapters.storage.local import LocalBlobStore
from polly_pipeline_server.adapters.storage.qdrant import QdrantVectorStore
from polly_pipeline_server.adapters.usage.memory_store import InMemoryBalanceStore, InMemoryJobStore
from polly_pipeline_server.domain.ingestion.use_cases import IngestDocument
from polly_pipeline_server.domain.rag.use_cases import ExecuteQuery


@lru_cache
def get_blob_store() -> LocalBlobStore:
    return LocalBlobStore(base_path=os.getenv("BLOB_STORAGE_PATH", "./data/blobs"))


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        collection=os.getenv("QDRANT_COLLECTION", "polly_chunks"),
        vector_size=int(os.getenv("EMBEDDING_DIMENSIONS", "768")),
    )


@lru_cache
def get_embedder() -> Embedder:
    return create_embedder()


@lru_cache
def get_llm_client() -> LLMClient:
    return create_llm_client()


@lru_cache
def get_cache() -> RedisCache:
    return RedisCache(url=os.getenv("REDIS_URL", "redis://localhost:6379/0"))


@lru_cache
def get_job_store() -> InMemoryJobStore:
    return InMemoryJobStore()


@lru_cache
def get_balance_store() -> InMemoryBalanceStore:
    return InMemoryBalanceStore()


@lru_cache
def get_text_extractor() -> ContentTypeExtractor:
    return ContentTypeExtractor()


def get_ingest_document_use_case() -> IngestDocument:
    return IngestDocument(
        blob_store=get_blob_store(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
        job_store=get_job_store(),
        text_extractor=get_text_extractor(),
    )


def get_execute_query_use_case() -> ExecuteQuery:
    return ExecuteQuery(
        embedder=get_embedder(),
        vector_store=get_vector_store(),
        llm_client=get_llm_client(),
        cache=get_cache(),
        cost_margin=float(os.getenv("COST_MARGIN", "0.4")),
    )


def get_session_id(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    fingerprint = f"{client_ip}|{user_agent}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
