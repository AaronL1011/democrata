import json
import os
from datetime import UTC, datetime
from uuid import UUID

import redis.asyncio as redis

from democrata_server.domain.ingestion.entities import Job, JobStatus, JobType


JOB_KEY_PREFIX = "ingestion:job:"
JOB_TTL_SECONDS = 7 * 24 * 60 * 60


def _job_to_dict(job: Job) -> dict:
    return {
        "id": str(job.id),
        "status": job.status.value,
        "progress_percent": job.progress_percent,
        "documents_processed": job.documents_processed,
        "chunks_created": job.chunks_created,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "job_type": job.job_type.value,
        "source_id": job.source_id,
    }


def _dict_to_job(data: dict) -> Job:
    return Job(
        id=UUID(data["id"]),
        status=JobStatus(data["status"]),
        progress_percent=data.get("progress_percent", 0),
        documents_processed=data.get("documents_processed", 0),
        chunks_created=data.get("chunks_created", 0),
        error_message=data.get("error_message"),
        created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")) if data.get("created_at") else datetime.now(UTC),
        completed_at=datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00")) if data.get("completed_at") else None,
        job_type=JobType(data.get("job_type", "upload")),
        source_id=data.get("source_id"),
    )


class RedisJobStore:
    def __init__(self, url: str | None = None):
        self._url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)
        return self._client

    def _key(self, job_id: UUID) -> str:
        return f"{JOB_KEY_PREFIX}{job_id}"

    async def save(self, job: Job) -> None:
        client = await self._get_client()
        data = json.dumps(_job_to_dict(job))
        await client.setex(self._key(job.id), JOB_TTL_SECONDS, data)

    async def get(self, job_id: UUID) -> Job | None:
        client = await self._get_client()
        data = await client.get(self._key(job_id))
        if data is None:
            return None
        return _dict_to_job(json.loads(data))
