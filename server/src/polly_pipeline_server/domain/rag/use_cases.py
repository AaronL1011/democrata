import time
from dataclasses import dataclass

from polly_pipeline_server.domain.ingestion.ports import Embedder, VectorStore
from polly_pipeline_server.domain.usage.entities import CostBreakdown

from .entities import Query, QueryMetadata, RAGResult
from .ports import Cache, LLMClient


@dataclass
class ExecuteQueryResult:
    result: RAGResult
    cost: CostBreakdown


class ExecuteQuery:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        llm_client: LLMClient,
        cache: Cache,
        top_k: int = 10,
        cache_ttl_seconds: int = 3600,
        cost_margin: float = 0.4,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.cache = cache
        self.top_k = top_k
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cost_margin = cost_margin

    async def execute(self, query: Query) -> ExecuteQueryResult:
        start_time = time.time()
        cache_key = self.cache.query_key(query)

        # Check cache
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return ExecuteQueryResult(
                result=cached,
                cost=CostBreakdown.zero(),
            )

        # Embed query
        query_embedding = await self.embedder.embed_single(query.text)
        embedding_tokens = len(query.text.split())  # Approximate

        # Search vector store
        filters = None
        if query.filters:
            filters = {}
            if query.filters.document_types:
                filters["document_type"] = query.filters.document_types
            if query.filters.date_from:
                filters["date_from"] = query.filters.date_from
            if query.filters.date_to:
                filters["date_to"] = query.filters.date_to

        chunks = await self.vector_store.search(
            vector=query_embedding, k=self.top_k, filters=filters
        )

        # Build context from chunks
        context = [chunk.text for chunk in chunks]

        # Generate response with LLM
        layout, components, token_usage = await self.llm_client.generate_response(
            query=query.text,
            context=context,
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Build result
        result = RAGResult(
            layout=layout,
            components=components,
            metadata=QueryMetadata(
                documents_retrieved=len(set(c.document_id for c in chunks)),
                chunks_used=len(chunks),
                processing_time_ms=processing_time_ms,
                model=token_usage.get("model", "unknown"),
            ),
            cached=False,
        )

        # Calculate cost
        cost = CostBreakdown.calculate(
            embedding_tokens=embedding_tokens,
            llm_input_tokens=token_usage.get("input_tokens", 0),
            llm_output_tokens=token_usage.get("output_tokens", 0),
            vector_queries=1,
            margin=self.cost_margin,
        )

        result.cost = cost

        # Cache result
        await self.cache.set(cache_key, result, self.cache_ttl_seconds)

        return ExecuteQueryResult(result=result, cost=cost)
