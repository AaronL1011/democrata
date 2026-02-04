class PlainTextExtractor:
    """Extracts text from plain text files using UTF-8 decoding."""

    def extract(self, content: bytes, content_type: str, filename: str) -> str:
        return content.decode("utf-8", errors="replace")
