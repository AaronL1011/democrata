"""LLM-based data extractor for grounded extraction from context."""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from polly_pipeline_server.domain.agents.entities import (
    ExtractionResult,
    IntentResult,
    SourceQuote,
)

from .prompts.extractor import EXTRACTION_PROMPTS, GENERIC_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class LLMDataExtractor:
    """Data extractor that uses an LLM to extract grounded, structured data."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o",
        temperature: float = 0.1,
    ):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
        )
        self.model = model

    async def extract(
        self,
        component_type: str,
        context: list[str],
        intent: IntentResult,
    ) -> ExtractionResult:
        """Extract structured data from context for a specific component type."""
        if not context:
            return ExtractionResult.empty(component_type, "No context available")

        prompt = self._build_prompt(component_type, context, intent)

        messages = [
            SystemMessage(content="You are a data extractor. Extract only facts explicitly stated in the context. Output JSON only."),
            HumanMessage(content=prompt),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            content = response.content
            return self._parse_extraction(content, component_type)
        except Exception as e:
            logger.warning(f"Extraction failed for {component_type}: {e}")
            return ExtractionResult.empty(component_type, str(e))

    def _build_prompt(
        self,
        component_type: str,
        context: list[str],
        intent: IntentResult,
    ) -> str:
        """Build the extraction prompt for the given component type."""
        prompt_template = EXTRACTION_PROMPTS.get(component_type, GENERIC_EXTRACTION_PROMPT)
        context_text = "\n\n---\n\n".join(context)

        # Build query focus from intent
        query_focus_parts = []
        if intent.entities.parties:
            query_focus_parts.append(f"Parties: {', '.join(intent.entities.parties)}")
        if intent.entities.members:
            query_focus_parts.append(f"Members: {', '.join(intent.entities.members)}")
        if intent.entities.bills:
            query_focus_parts.append(f"Bills: {', '.join(intent.entities.bills)}")
        if intent.entities.topics:
            query_focus_parts.append(f"Topics: {', '.join(intent.entities.topics)}")

        query_focus = "; ".join(query_focus_parts) if query_focus_parts else "General query"

        # Format the prompt
        format_kwargs: dict[str, Any] = {
            "context": context_text,
            "query_focus": query_focus,
        }

        # Add entities for comparison prompts
        if component_type == "comparison" and intent.entities.parties:
            format_kwargs["entities"] = ", ".join(intent.entities.parties)
        elif component_type == "comparison":
            format_kwargs["entities"] = "entities mentioned in context"

        # Handle component_type for generic prompt
        if component_type not in EXTRACTION_PROMPTS:
            format_kwargs["component_type"] = component_type

        return prompt_template.format(**format_kwargs)

    def _parse_extraction(self, content: str, component_type: str) -> ExtractionResult:
        """Parse LLM response into ExtractionResult."""
        try:
            json_str = self._extract_json(content)
            data = json.loads(json_str)
            return self._build_extraction_result(data, component_type)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse extraction response: {e}")
            return ExtractionResult.empty(component_type, f"Parse error: {e}")

    def _extract_json(self, content: str) -> str:
        """Extract JSON from response, handling markdown code blocks."""
        if "```json" in content:
            return content.split("```json")[1].split("```")[0]
        elif "```" in content:
            return content.split("```")[1].split("```")[0]
        return content

    def _build_extraction_result(self, data: dict[str, Any], component_type: str) -> ExtractionResult:
        """Build ExtractionResult from parsed JSON data."""
        # Extract source quotes
        source_quotes_raw = data.pop("source_quotes", [])
        source_quotes = [
            SourceQuote(text=quote) if isinstance(quote, str) else SourceQuote(
                text=quote.get("text", str(quote)),
                chunk_index=quote.get("chunk_index"),
                document_id=quote.get("document_id"),
            )
            for quote in source_quotes_raw
        ]

        # Extract completeness and warnings
        completeness = float(data.pop("completeness", 1.0))
        completeness = max(0.0, min(1.0, completeness))
        warnings = data.pop("warnings", [])

        return ExtractionResult(
            component_type=component_type,
            extracted_data=data,
            source_quotes=source_quotes,
            completeness=completeness,
            warnings=warnings if isinstance(warnings, list) else [str(warnings)],
        )
