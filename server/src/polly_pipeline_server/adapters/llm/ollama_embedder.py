import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0


class OllamaEmbeddingError(Exception):
    """Raised when Ollama embedding fails."""

    def __init__(self, message: str, chunk_index: int | None = None, response_body: str | None = None):
        self.chunk_index = chunk_index
        self.response_body = response_body
        super().__init__(message)


class OllamaEmbedder:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        client = await self._get_client()
        embeddings = []

        for i, text in enumerate(texts):
            embedding = await self._embed_with_retry(client, text, i, len(texts))
            embeddings.append(embedding)

            # Log progress every 50 chunks
            if (i + 1) % 50 == 0:
                logger.info(f"Embedded {i + 1}/{len(texts)} chunks")

        logger.info(f"Successfully embedded {len(embeddings)} chunks")
        return embeddings

    async def _embed_with_retry(
        self, client: httpx.AsyncClient, text: str, chunk_index: int, total_chunks: int
    ) -> list[float]:
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={
                        "model": self.model,
                        "input": text,
                    },
                )

                if response.is_success:
                    data = response.json()
                    return data["embeddings"][0]

                response_body = response.text

                # If it's a 500 error (Ollama crash), retry after delay
                if response.status_code >= 500 and attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        f"Ollama error for chunk {chunk_index}/{total_chunks} (attempt {attempt + 1}): "
                        f"{response_body[:200]}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(
                    f"Ollama embedding failed for chunk {chunk_index}/{total_chunks}: "
                    f"status={response.status_code}, body={response_body[:500]}"
                )
                raise OllamaEmbeddingError(
                    f"Ollama returned {response.status_code} for chunk {chunk_index}/{total_chunks}: {response_body[:500]}",
                    chunk_index=chunk_index,
                    response_body=response_body,
                )

            except httpx.RequestError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        f"Network error for chunk {chunk_index}/{total_chunks} (attempt {attempt + 1}): "
                        f"{e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"Network error during embedding chunk {chunk_index}/{total_chunks}: {e}")
                raise OllamaEmbeddingError(
                    f"Network error embedding chunk {chunk_index}/{total_chunks}: {e}",
                    chunk_index=chunk_index,
                ) from e

        # Should not reach here, but just in case
        raise OllamaEmbeddingError(
            f"Failed to embed chunk {chunk_index}/{total_chunks} after {MAX_RETRIES} attempts",
            chunk_index=chunk_index,
        )

    async def embed_single(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0] if embeddings else []

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
