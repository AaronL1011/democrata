import os

import pytest

from democrata_server.adapters.llm.config import EmbeddingConfig, EmbeddingProvider
from democrata_server.adapters.llm.embedder import OpenAIEmbedder
from democrata_server.adapters.llm.factory import create_embedder
from democrata_server.adapters.llm.ollama_embedder import OllamaEmbedder


class TestEmbeddingConfig:
    def test_openai_config(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-large")

        config = EmbeddingConfig.from_env()

        assert config.provider == EmbeddingProvider.OPENAI
        assert config.model == "text-embedding-3-large"

    def test_ollama_config(self, monkeypatch):
        monkeypatch.setenv("EMBEDDING_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

        config = EmbeddingConfig.from_env()

        assert config.provider == EmbeddingProvider.OLLAMA
        assert config.model == "nomic-embed-text"


class TestFactory:
    def test_create_openai_embedder(self):
        config = EmbeddingConfig(
            provider=EmbeddingProvider.OPENAI,
            model="text-embedding-3-small",
            api_key="test-key",
        )

        embedder = create_embedder(config)

        assert isinstance(embedder, OpenAIEmbedder)

    def test_create_ollama_embedder(self):
        config = EmbeddingConfig(
            provider=EmbeddingProvider.OLLAMA,
            model="nomic-embed-text",
            base_url="http://localhost:11434",
        )

        embedder = create_embedder(config)

        assert isinstance(embedder, OllamaEmbedder)


class TestOllamaClients:
    def test_ollama_embedder_initialization(self):
        embedder = OllamaEmbedder(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
        )

        assert embedder.base_url == "http://localhost:11434"
        assert embedder.model == "nomic-embed-text"
