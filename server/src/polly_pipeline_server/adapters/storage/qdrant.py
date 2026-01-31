from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from polly_pipeline_server.domain.ingestion.entities import Chunk


class QdrantVectorStore:
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection: str = "polly_chunks",
        vector_size: int = 768,
    ):
        self.client = QdrantClient(url=url)
        self.collection = collection
        self.vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        points = [
            PointStruct(
                id=str(chunk.id),
                vector=chunk.embedding or [],
                payload={
                    "document_id": str(chunk.document_id),
                    "text": chunk.text,
                    "position": chunk.position,
                    **chunk.metadata,
                },
            )
            for chunk in chunks
            if chunk.embedding
        ]

        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    async def search(
        self, vector: list[float], k: int = 10, filters: dict | None = None
    ) -> list[Chunk]:
        results = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=k,
        )

        chunks = []
        for result in results.points:
            payload = result.payload or {}
            chunks.append(
                Chunk(
                    id=UUID(result.id) if isinstance(result.id, str) else UUID(int=result.id),
                    document_id=UUID(payload.get("document_id", "")),
                    text=payload.get("text", ""),
                    position=payload.get("position", 0),
                    metadata={
                        k: v
                        for k, v in payload.items()
                        if k not in ("document_id", "text", "position")
                    },
                )
            )
        return chunks

    async def delete_by_document(self, document_id: UUID) -> None:
        self.client.delete(
            collection_name=self.collection,
            points_selector={
                "filter": {"must": [{"key": "document_id", "match": {"value": str(document_id)}}]}
            },
        )
