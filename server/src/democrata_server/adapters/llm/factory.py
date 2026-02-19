from typing import Protocol, runtime_checkable

from .config import EmbeddingConfig, EmbeddingProvider


@runtime_checkable
class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_single(self, text: str) -> list[float]: ...


def create_embedder(config: EmbeddingConfig | None = None) -> Embedder:
    if config is None:
        config = EmbeddingConfig.from_env()

    if config.provider == EmbeddingProvider.OPENAI:
        from .embedder import OpenAIEmbedder

        return OpenAIEmbedder(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
        )
    elif config.provider == EmbeddingProvider.OLLAMA:
        from .ollama_embedder import OllamaEmbedder

        return OllamaEmbedder(
            base_url=config.base_url or "http://localhost:11434",
            model=config.model,
        )
    else:
        raise ValueError(f"Unsupported embedding provider: {config.provider}")
