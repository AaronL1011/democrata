"""LLM-based data extractor for grounded extraction from context."""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from democrata_server.domain.agents.entities import (
    ExtractionResult,
    IntentResult,
    SourceQuote,
)

from .prompts.extractor import EXTRACTION_PROMPTS, GENERIC_EXTRACTION_PROMPT
from .schemas import BaseExtractionSchema, get_extraction_schema

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
    ) -> tuple[ExtractionResult, dict]:
        """Extract structured data from context. Returns (ExtractionResult, token_usage)."""
        if not context:
            return ExtractionResult.empty(component_type, "No context available"), {
                "input_tokens": 0,
                "output_tokens": 0,
                "model": self.model,
            }

        prompt = self._build_prompt(component_type, context, intent)
        messages = [
            SystemMessage(
                content="You are a data extractor. Extract only facts explicitly stated in the context. Output valid JSON only."
            ),
            HumanMessage(content=prompt),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            token_usage = self._extract_token_usage(response)
            schema_class = get_extraction_schema(component_type)
            data = self._parse_json_content(
                response.content if isinstance(response.content, str) else str(response.content),
                schema_class,
            )
            result = self._build_extraction_result(data, component_type)
            return result, token_usage
        except Exception as e:
            logger.warning(f"Extraction failed for {component_type}: {e}")
            return ExtractionResult.empty(component_type, str(e)), {
                "input_tokens": 0,
                "output_tokens": 0,
                "model": self.model,
            }

    def _extract_token_usage(self, response) -> dict:
        """Extract token usage from LangChain response metadata."""
        usage = {}
        if hasattr(response, "response_metadata") and response.response_metadata:
            usage = response.response_metadata.get("token_usage") or response.response_metadata.get("usage") or {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
        if isinstance(usage, dict):
            return {
                "input_tokens": usage.get("input_tokens") or usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("output_tokens") or usage.get("completion_tokens", 0),
                "model": self.model,
            }
        return {
            "input_tokens": getattr(usage, "input_tokens", 0) or getattr(usage, "prompt_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0) or getattr(usage, "completion_tokens", 0),
            "model": self.model,
        }

    def _parse_json_content(self, content: str, schema_class: type[BaseExtractionSchema]) -> BaseExtractionSchema:
        """Extract JSON from response and validate against schema."""
        text = content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text)
        return schema_class.model_validate(data)

    def _parse_extraction(self, content: str, component_type: str) -> ExtractionResult:
        """Parse response content to ExtractionResult. Returns empty result on parse failure."""
        try:
            schema_class = get_extraction_schema(component_type)
            data = self._parse_json_content(content, schema_class)
            return self._build_extraction_result(data, component_type)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
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

    def _build_extraction_result(
        self, data: BaseExtractionSchema, component_type: str
    ) -> ExtractionResult:
        """Build ExtractionResult from structured output schema."""
        # Extract source quotes
        source_quotes = [SourceQuote(text=quote) for quote in data.source_quotes]

        # Convert schema to dict for extracted_data, excluding base fields
        data_dict = data.model_dump(exclude={"source_quotes", "completeness", "warnings"})

        return ExtractionResult(
            component_type=component_type,
            extracted_data=data_dict,
            source_quotes=source_quotes,
            completeness=data.completeness,
            warnings=data.warnings,
        )
