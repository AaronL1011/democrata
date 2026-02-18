"""LLM-based query planner for intent classification and entity extraction."""

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from democrata_server.domain.agents.entities import (
    ExtractedEntities,
    IntentResult,
    QueryType,
    ResponseDepth,
    RetrievalStrategy,
)

from .prompts.planner import PLANNER_PROMPT
from .schemas import PlannerOutputSchema

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

    async def analyze(self, query: str) -> tuple[IntentResult, dict]:
        """Classify query intent and extract entities. Returns (IntentResult, token_usage)."""
        prompt = PLANNER_PROMPT.format(query=query)

        messages = [
            SystemMessage(
                content="You are a query analyzer for an Australian political information system. "
                "Output valid JSON matching the schema."
            ),
            HumanMessage(content=prompt),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            token_usage = self._extract_token_usage(response)
            content = response.content if isinstance(response.content, str) else str(response.content)
            data = self._parse_json_content(content)
            result = PlannerOutputSchema.model_validate(data)
            return self._build_intent_result(result, query), token_usage
        except Exception as e:
            logger.warning(f"Planner failed, using default intent: {e}")
            return IntentResult.default_factual(query), {"input_tokens": 0, "output_tokens": 0, "model": self.model}

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

    def _parse_json_content(self, content: str) -> dict:
        """Extract JSON from response, handling markdown code blocks."""
        text = content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)

    def _parse_intent(self, content: str, original_query: str) -> IntentResult:
        """Parse response content to IntentResult. Returns default_factual on parse failure."""
        try:
            data = self._parse_json_content(content)
            result = PlannerOutputSchema.model_validate(data)
            return self._build_intent_result(result, original_query)
        except (json.JSONDecodeError, ValueError, KeyError):
            return IntentResult.default_factual(original_query)

    def _build_intent_result(self, data: PlannerOutputSchema, original_query: str) -> IntentResult:
        """Build IntentResult from structured output schema."""
        # Parse query type
        try:
            query_type = QueryType(data.query_type)
        except ValueError:
            query_type = QueryType.FACTUAL

        # Parse retrieval strategy
        try:
            retrieval_strategy = RetrievalStrategy(data.retrieval_strategy)
        except ValueError:
            retrieval_strategy = RetrievalStrategy.SINGLE_FOCUS

        # Parse entities from the nested schema
        entities = ExtractedEntities(
            parties=data.entities.parties,
            members=data.entities.members,
            bills=data.entities.bills,
            topics=data.entities.topics,
            date_from=data.entities.date_from,
            date_to=data.entities.date_to,
            document_types=data.entities.document_types,
        )

        # Parse expected components
        expected_components = data.expected_components or ["text_block"]

        # Parse rewritten queries
        rewritten_queries = data.rewritten_queries or [original_query]

        # Parse response depth
        try:
            response_depth = ResponseDepth(data.response_depth)
        except ValueError:
            response_depth = ResponseDepth.STANDARD

        return IntentResult(
            query_type=query_type,
            entities=entities,
            expected_components=expected_components,
            retrieval_strategy=retrieval_strategy,
            rewritten_queries=rewritten_queries,
            confidence=data.confidence,
            response_depth=response_depth,
        )
