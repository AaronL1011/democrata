from typing import Any
from uuid import UUID

from democrata_server.domain.ingestion.entities import Job, SourceConfig
from democrata_server.domain.ingestion.ports import JobStore
from democrata_server.domain.ingestion.use_cases import IngestDocument


class ExecuteScrapeRun:
    """Orchestrate a scrape run: fetch documents from source, ingest each via IngestDocument."""

    def __init__(
        self,
        ingest_use_case: IngestDocument,
        job_store: JobStore,
    ):
        self._ingest = ingest_use_case
        self._job_store = job_store

    async def execute(
        self,
        job_id: UUID,
        config: SourceConfig,
        fetcher: Any,
    ) -> Job:
        """Run scrape for config using the provided fetcher. Fetcher must have async fetch(config) yielding ScrapedDocument."""
        job = await self._job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.start()
        await self._job_store.save(job)

        total_docs = 0
        total_chunks = 0

        try:
            async for scraped in fetcher.fetch(config):
                await self._ingest.execute(
                    content=scraped.content,
                    filename=scraped.filename,
                    content_type=scraped.content_type,
                    metadata=scraped.metadata,
                    existing_job=job,
                )
                total_docs = job.documents_processed
                total_chunks = job.chunks_created

            job.complete(documents=total_docs, chunks=total_chunks)
            await self._job_store.save(job)
        except Exception as e:
            job.fail(str(e))
            await self._job_store.save(job)
            raise
        finally:
            if hasattr(fetcher, "close"):
                await fetcher.close()

        return job
