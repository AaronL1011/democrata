import asyncio
from urllib.parse import urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser
from tenacity import retry, stop_after_attempt, wait_exponential

from democrata_server.domain.ingestion.entities import (
    DocumentMetadata,
    DocumentType,
    ScrapedDocument,
    SourceConfig,
)

from . import register_fetcher


def _extract_text_from_html(html: str, selector: str | None) -> str:
    """Extract text from HTML using optional CSS selector."""
    parser = HTMLParser(html)
    if selector:
        node = parser.css_first(selector)
        return node.text(separator="\n", deep=True) if node else ""
    body = parser.body
    return body.text(separator="\n", deep=True) if body else ""


def _filename_from_url(url: str, content_type: str) -> str:
    """Derive filename from URL and content type."""
    path = urlparse(url).path
    if path and path != "/":
        name = path.rstrip("/").split("/")[-1]
        if name and "." in name:
            return name
    if "pdf" in content_type.lower():
        return "document.pdf"
    return "document.html"


@register_fetcher("configurable_http")
class ConfigurableHttpFetcher:
    """Config-driven HTTP fetcher for HTML and PDF. Uses tenacity retries and configurable delay."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _fetch_url(self, url: str) -> tuple[bytes, str]:
        """Fetch URL with retries. Returns (content, content_type)."""
        response = await self._client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "application/octet-stream").split(";")[0].strip()
        return response.content, content_type

    async def fetch(self, config: SourceConfig):
        """Fetch documents from config URL(s). Yields ScrapedDocument per document."""
        urls = config.urls or [config.url]
        delay = float(config.options.get("delay_seconds", 1.0))
        content_selector = config.options.get("content_selector")
        link_selector = config.options.get("link_selector")

        for url in urls:
            await asyncio.sleep(delay)
            content, content_type = await self._fetch_url(url)

            if "text/html" in content_type or "application/xhtml" in content_type:
                html = content.decode("utf-8", errors="replace")
                if link_selector:
                    parser = HTMLParser(html)
                    for node in parser.css(link_selector):
                        href = node.attributes.get("href")
                        if href:
                            doc_url = urljoin(url, href)
                            await asyncio.sleep(delay)
                            try:
                                doc_content, doc_type = await self._fetch_url(doc_url)
                                if "text/html" in doc_type:
                                    text = _extract_text_from_html(
                                        doc_content.decode("utf-8", errors="replace"),
                                        content_selector,
                                    )
                                elif "pdf" in doc_type.lower():
                                    text = ""
                                    from democrata_server.adapters.extraction import ContentTypeExtractor
                                    extractor = ContentTypeExtractor()
                                    text = extractor.extract(doc_content, doc_type, _filename_from_url(doc_url, doc_type))
                                else:
                                    text = doc_content.decode("utf-8", errors="replace")
                                if text.strip():
                                    yield ScrapedDocument(
                                        content=doc_content if "pdf" in doc_type.lower() else text,
                                        metadata=DocumentMetadata(
                                            document_type=config.document_type,
                                            source=config.id,
                                            source_url=doc_url,
                                            title=doc_url.split("/")[-1] or "document",
                                        ),
                                        content_type=doc_type,
                                        filename=_filename_from_url(doc_url, doc_type),
                                    )
                            except Exception:
                                continue
                else:
                    text = _extract_text_from_html(html, content_selector)
                    if text.strip():
                        yield ScrapedDocument(
                            content=text,
                            metadata=DocumentMetadata(
                                document_type=config.document_type,
                                source=config.id,
                                source_url=url,
                                title=url.split("/")[-1] or "document",
                            ),
                            content_type="text/html",
                            filename=_filename_from_url(url, content_type),
                        )
            elif "pdf" in content_type.lower():
                from democrata_server.adapters.extraction import ContentTypeExtractor
                extractor = ContentTypeExtractor()
                text = extractor.extract(content, content_type, _filename_from_url(url, content_type))
                if text.strip():
                    yield ScrapedDocument(
                        content=content,
                        metadata=DocumentMetadata(
                            document_type=config.document_type,
                            source=config.id,
                            source_url=url,
                            title=_filename_from_url(url, content_type),
                        ),
                        content_type=content_type,
                        filename=_filename_from_url(url, content_type),
                    )
