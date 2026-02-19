import os
from pathlib import Path

import yaml

from democrata_server.domain.ingestion.entities import DocumentType, SourceConfig


def load_scrape_config(jurisdiction: str | None = None) -> dict:
    """Load scrape config from config/scrape_{jurisdiction}.yaml."""
    jurisdiction = jurisdiction or os.getenv("JURISDICTION", "au")
    if config_dir_env := os.getenv("SCRAPE_CONFIG_DIR"):
        config_dir = Path(config_dir_env)
    else:
        config_dir = Path.cwd() / "config"
        if not config_dir.exists():
            server_dir = Path(__file__).parent.parent.parent.parent.parent
            config_dir = server_dir / "config"
    config_path = config_dir / f"scrape_{jurisdiction}.yaml"
    if not config_path.exists():
        return {"jurisdiction": jurisdiction, "sources": []}
    with config_path.open() as f:
        return yaml.safe_load(f) or {"jurisdiction": jurisdiction, "sources": []}


def parse_source_config(raw: dict) -> SourceConfig:
    """Parse a raw source dict from YAML into SourceConfig."""
    doc_type_str = raw.get("type", "other")
    try:
        doc_type = DocumentType(doc_type_str)
    except ValueError:
        doc_type = DocumentType.OTHER
    return SourceConfig(
        id=raw["id"],
        document_type=doc_type,
        scraper=raw["scraper"],
        url=raw.get("url", ""),
        urls=raw.get("urls"),
        schedule=raw.get("schedule"),
        options=raw.get("options") or {},
    )


def get_source_config(source_id: str, jurisdiction: str | None = None) -> SourceConfig | None:
    """Get source config by id from the scrape config."""
    config = load_scrape_config(jurisdiction)
    for raw in config.get("sources", []):
        if raw.get("id") == source_id:
            return parse_source_config(raw)
    return None


_FETCHER_REGISTRY: dict[str, type] = {}


def register_fetcher(key: str):
    """Decorator to register a SourceFetcher implementation."""

    def decorator(cls: type) -> type:
        _FETCHER_REGISTRY[key] = cls
        return cls

    return decorator


def get_fetcher(key: str):
    """Get fetcher class by key from registry."""
    return _FETCHER_REGISTRY.get(key)


from . import configurable_http  # noqa: E402 - registers fetcher
