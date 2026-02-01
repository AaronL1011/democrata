"""LLM-based query planner for intent classification and entity extraction."""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from polly_pipeline_server.domain.agents.entities import (
    ExtractedEntities,
    IntentResult,
    QueryType,
    RetrievalStrategy,
)

from .prompts.planner import PLANNER_PROMPT

logger = logging.getLogger(__name__)


class LLMQueryPlanner:
    """Query planner that uses an LLM to classify intent and extract entities."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
        )
        self.model = model

    async def analyze(self, query: str) -> IntentResult:
        """Classify query intent and extract entities."""
        prompt = PLANNER_PROMPT.format(query=query)

        messages = [
            SystemMessage(content="You are a query analyzer. Output JSON only."),
            HumanMessage(content=prompt),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            content = response.content
            return self._parse_intent(content, query)
        except Exception as e:
            logger.warning(f"Planner failed, using default intent: {e}")
            return IntentResult.default_factual(query)

    def _parse_intent(self, content: str, original_query: str) -> IntentResult:
        """Parse LLM response into IntentResult."""
        try:
            json_str = self._extract_json(content)
            data = json.loads(json_str)
            return self._build_intent_result(data, original_query)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse planner response: {e}")
            return IntentResult.default_factual(original_query)

    def _extract_json(self, content: str) -> str:
        """Extract JSON from response, handling markdown code blocks."""
        if "```json" in content:
            return content.split("```json")[1].split("```")[0]
        elif "```" in content:
            return content.split("```")[1].split("```")[0]
        return content

    def _build_intent_result(self, data: dict[str, Any], original_query: str) -> IntentResult:
        """Build IntentResult from parsed JSON data."""
        # Parse query type
        query_type_str = data.get("query_type", "factual")
        try:
            query_type = QueryType(query_type_str)
        except ValueError:
            query_type = QueryType.FACTUAL

        # Parse retrieval strategy
        strategy_str = data.get("retrieval_strategy", "single_focus")
        try:
            retrieval_strategy = RetrievalStrategy(strategy_str)
        except ValueError:
            retrieval_strategy = RetrievalStrategy.SINGLE_FOCUS

        # Parse entities
        entities_data = data.get("entities", {})
        entities = ExtractedEntities(
            parties=entities_data.get("parties", []),
            members=entities_data.get("members", []),
            bills=entities_data.get("bills", []),
            topics=entities_data.get("topics", []),
            date_from=entities_data.get("date_from"),
            date_to=entities_data.get("date_to"),
            document_types=entities_data.get("document_types", []),
        )

        # Parse expected components
        expected_components = data.get("expected_components", ["text_block"])
        if not expected_components:
            expected_components = ["text_block"]

        # Parse rewritten queries
        rewritten_queries = data.get("rewritten_queries", [original_query])
        if not rewritten_queries:
            rewritten_queries = [original_query]

        # Parse confidence
        confidence = float(data.get("confidence", 0.8))
        confidence = max(0.0, min(1.0, confidence))

        return IntentResult(
            query_type=query_type,
            entities=entities,
            expected_components=expected_components,
            retrieval_strategy=retrieval_strategy,
            rewritten_queries=rewritten_queries,
            confidence=confidence,
        )
