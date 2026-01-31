from typing import Any, Protocol

from .entities import Component, Layout, Query


class LLMClient(Protocol):
    async def generate_response(
        self, query: str, context: list[str], system_prompt: str | None = None
    ) -> tuple[Layout, list[Component], dict[str, int]]:
        """
        Generate a structured RAG response.

        Returns:
            Layout, Components, and token usage dict with keys:
            - input_tokens
            - output_tokens
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
