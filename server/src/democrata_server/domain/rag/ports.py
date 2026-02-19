from typing import Any, Protocol

from .entities import Component, Layout, Query, RetrievalResult


class ContextRetriever(Protocol):
    """Retrieves context using intent-driven strategies."""

    async def retrieve(
        self,
        query: str,
        intent: Any,  # IntentResult from agents domain
    ) -> RetrievalResult:
        """
        Retrieve context chunks based on query and classified intent.

        Args:
            query: The user's natural language query.
            intent: The classified intent with entities and retrieval strategy.

        Returns:
            RetrievalResult with chunks and coverage metrics.
        """
        ...


class Cache(Protocol):
    async def get(self, key: str) -> Any | None:
        """Get cached value by key."""
        ...

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set cached value with optional TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Delete cached value."""
        ...

    def query_key(self, query: Query) -> str:
        """Generate a cache key for a query."""
        ...
