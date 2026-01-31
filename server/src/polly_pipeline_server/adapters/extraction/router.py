from .pdf import PdfExtractor
from .plain import PlainTextExtractor


class ContentTypeExtractor:
    """Routes extraction to the appropriate extractor based on content type."""

    def __init__(self):
        self._pdf_extractor = PdfExtractor()
        self._plain_extractor = PlainTextExtractor()
        self._extractors = {
            "application/pdf": self._pdf_extractor,
            "text/plain": self._plain_extractor,
            "text/html": self._plain_extractor,
            "text/csv": self._plain_extractor,
            "text/markdown": self._plain_extractor,
            "application/json": self._plain_extractor,
        }

    def extract(self, content: bytes, content_type: str, filename: str) -> str:
        # Check by content type first
        extractor = self._extractors.get(content_type)

        # Fall back to file extension detection
        if extractor is None:
            if filename.lower().endswith(".pdf"):
                extractor = self._pdf_extractor
            else:
                extractor = self._plain_extractor

        return extractor.extract(content, content_type, filename)
