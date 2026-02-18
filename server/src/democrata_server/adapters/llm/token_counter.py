"""Token counting utilities for cost calculation."""

import logging

logger = logging.getLogger(__name__)


def count_tokens(texts: list[str], model: str = "cl100k_base") -> int:
    """
    Count tokens in a list of texts using tiktoken.

    Uses cl100k_base encoding (OpenAI GPT-4, text-embedding-3-*) by default.
    """
    try:
        import tiktoken

        enc = tiktoken.get_encoding(model)
        return sum(len(enc.encode(t)) for t in texts)
    except Exception as e:
        logger.warning(f"Token counting failed, using word estimate: {e}")
        return sum(max(1, len(t.split())) for t in texts)
