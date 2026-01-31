from typing import Protocol, runtime_checkable

from .config import EmbeddingConfig, EmbeddingProvider, LLMConfig, LLMProvider


@runtime_checkable
class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_single(self, text: str) -> list[float]: ...


@runtime_checkable
class LLMClient(Protocol):
    async def generate_response(
        self, query: str, context: list[str], system_prompt: str | None = None
    ) -> tuple: ...


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


def create_llm_client(config: LLMConfig | None = None) -> LLMClient:
    if config is None:
        config = LLMConfig.from_env()

    if config.provider == LLMProvider.OPENAI:
        from .langchain_client import LangChainLLMClient

        return LangChainLLMClient(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            temperature=config.temperature,
        )
    elif config.provider == LLMProvider.OLLAMA:
        from .ollama_client import OllamaLLMClient

        return OllamaLLMClient(
            base_url=config.base_url or "http://localhost:11434",
            model=config.model,
            temperature=config.temperature,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
