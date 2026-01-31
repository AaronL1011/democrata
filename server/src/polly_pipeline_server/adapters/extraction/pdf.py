from io import BytesIO

from pypdf import PdfReader


class PdfExtractor:
    """Extracts text from PDF files using pypdf."""

    def extract(self, content: bytes, content_type: str, filename: str) -> str:
        reader = PdfReader(BytesIO(content))
        text_parts: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n\n".join(text_parts)
