from collections.abc import AsyncIterator
from typing import Protocol
from uuid import UUID

from .entities import Chunk, DocumentMetadata, Job, ScrapedDocument, SourceConfig


class BlobStore(Protocol):
    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Store blob, return the key/reference."""
        ...

    async def get(self, key: str) -> bytes:
        """Retrieve blob by key."""
        ...

    async def delete(self, key: str) -> None:
        """Delete blob by key."""
        ...


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        ...

    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        ...


class VectorStore(Protocol):
    async def upsert(self, chunks: list[Chunk]) -> None:
        """Insert or update chunks with their embeddings."""
        ...

    async def search(
        self, vector: list[float], k: int = 10, filters: dict | None = None
    ) -> list[Chunk]:
        """Find top-k similar chunks."""
        ...

    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks for a document."""
        ...


class ChunkStore(Protocol):
    """Persistent storage for chunk metadata (separate from vector index)."""

    async def save(self, chunk: Chunk) -> None: ...

    async def get(self, chunk_id: UUID) -> Chunk | None: ...

    async def get_by_document(self, document_id: UUID) -> list[Chunk]: ...


class JobStore(Protocol):
    async def save(self, job: Job) -> None: ...

    async def get(self, job_id: UUID) -> Job | None: ...


class SourceFetcher(Protocol):
    """Fetch documents from an external source. Yields ScrapedDocument per document."""

    async def fetch(self, config: SourceConfig) -> AsyncIterator["ScrapedDocument"]:
        ...


class TextExtractor(Protocol):
    def extract(self, content: bytes, content_type: str, filename: str) -> str:
        """Extract text from binary content based on content type."""
        ...
