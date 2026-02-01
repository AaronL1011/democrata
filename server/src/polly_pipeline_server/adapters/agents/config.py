"""Configuration for agent adapters."""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for the agent pipeline."""

    # Model selection for each agent
    planner_model: str
    extractor_model: str
    composer_model: str
    verifier_model: str

    # Feature flags
    verifier_enabled: bool

    # API configuration
    openai_api_key: str | None
    openai_base_url: str | None

    # Retrieval configuration
    default_top_k: int
    min_chunks_for_sufficiency: int

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            # Models - use fast models for planner/verifier, capable for extractor/composer
            planner_model=os.getenv("AGENT_PLANNER_MODEL", "gpt-4o-mini"),
            extractor_model=os.getenv("AGENT_EXTRACTOR_MODEL", "gpt-4o"),
            composer_model=os.getenv("AGENT_COMPOSER_MODEL", "gpt-4o"),
            verifier_model=os.getenv("AGENT_VERIFIER_MODEL", "gpt-4o-mini"),
            # Feature flags
            verifier_enabled=os.getenv("AGENT_VERIFIER_ENABLED", "true").lower() == "true",
            # API configuration
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            # Retrieval
            default_top_k=int(os.getenv("AGENT_DEFAULT_TOP_K", "20")),
            min_chunks_for_sufficiency=int(os.getenv("AGENT_MIN_CHUNKS", "3")),
        )
