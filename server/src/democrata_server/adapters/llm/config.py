import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EmbeddingProvider(Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"


@dataclass
class EmbeddingConfig:
    provider: EmbeddingProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    dimensions: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        provider_str = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
        provider = EmbeddingProvider(provider_str)

        if provider == EmbeddingProvider.OPENAI:
            return cls(
                provider=provider,
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
                dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
            )
        elif provider == EmbeddingProvider.OLLAMA:
            return cls(
                provider=provider,
                model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "768")),
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {provider_str}")
