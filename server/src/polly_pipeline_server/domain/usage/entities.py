from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


# Cost rates (per 1K tokens, in cents)
EMBEDDING_RATE_CENTS = 0.01  # ~$0.0001 per 1K tokens
LLM_INPUT_RATE_CENTS = 1.0  # ~$0.01 per 1K tokens
LLM_OUTPUT_RATE_CENTS = 3.0  # ~$0.03 per 1K tokens
VECTOR_QUERY_RATE_CENTS = 0.01  # ~$0.0001 per query


class UsageEventType(str, Enum):
    QUERY = "query"
    INGESTION = "ingestion"


@dataclass
class CostBreakdown:
    embedding_tokens: int = 0
    embedding_cost_cents: int = 0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    llm_cost_cents: int = 0
    vector_queries: int = 0
    vector_cost_cents: int = 0
    margin_cents: int = 0
    total_cents: int = 0
    total_credits: int = 0  # 1 credit = 1 cent

    @classmethod
    def zero(cls) -> "CostBreakdown":
        return cls()

    @classmethod
    def calculate(
        cls,
        embedding_tokens: int = 0,
        llm_input_tokens: int = 0,
        llm_output_tokens: int = 0,
        vector_queries: int = 0,
        margin: float = 0.4,
    ) -> "CostBreakdown":
        # Use float arithmetic then round at the end to avoid losing small values
        embedding_cost_f = (embedding_tokens / 1000) * EMBEDDING_RATE_CENTS
        llm_input_cost_f = (llm_input_tokens / 1000) * LLM_INPUT_RATE_CENTS
        llm_output_cost_f = (llm_output_tokens / 1000) * LLM_OUTPUT_RATE_CENTS
        llm_cost_f = llm_input_cost_f + llm_output_cost_f
        vector_cost_f = vector_queries * VECTOR_QUERY_RATE_CENTS

        subtotal_f = embedding_cost_f + llm_cost_f + vector_cost_f
        margin_f = subtotal_f * margin
        total_f = subtotal_f + margin_f

        # Round to nearest cent, minimum 1 cent if any cost was incurred
        embedding_cost = max(1, round(embedding_cost_f)) if embedding_tokens > 0 else 0
        llm_cost = max(1, round(llm_cost_f)) if (llm_input_tokens + llm_output_tokens) > 0 else 0
        vector_cost = max(1, round(vector_cost_f)) if vector_queries > 0 else 0
        margin_cents = max(1, round(margin_f)) if margin > 0 and subtotal_f > 0 else 0
        total = round(total_f) if total_f > 0 else 0

        return cls(
            embedding_tokens=embedding_tokens,
            embedding_cost_cents=embedding_cost,
            llm_input_tokens=llm_input_tokens,
            llm_output_tokens=llm_output_tokens,
            llm_cost_cents=llm_cost,
            vector_queries=vector_queries,
            vector_cost_cents=vector_cost,
            margin_cents=margin_cents,
            total_cents=total,
            total_credits=total,
        )


@dataclass
class UsageEvent:
    id: UUID
    event_type: UsageEventType
    session_id: str
    user_id: UUID | None = None
    timestamp: datetime = field(default_factory=utc_now)
    query_hash: str | None = None
    query_preview: str | None = None  # Truncated for privacy
    cached: bool = False
    cost: CostBreakdown = field(default_factory=CostBreakdown.zero)
    credits_charged: int = 0

    @classmethod
    def create_query_event(
        cls,
        session_id: str,
        query: str,
        cost: CostBreakdown,
        cached: bool = False,
        user_id: UUID | None = None,
    ) -> "UsageEvent":
        return cls(
            id=uuid4(),
            event_type=UsageEventType.QUERY,
            session_id=session_id,
            user_id=user_id,
            query_hash=str(hash(query)),
            query_preview=query[:50] + "..." if len(query) > 50 else query,
            cached=cached,
            cost=cost,
            credits_charged=0 if cached else cost.total_credits,
        )


@dataclass
class UserBalance:
    user_id: UUID | None  # None for anonymous session-based tracking
    session_id: str | None
    credits: int = 0
    free_tier_remaining: int = 10  # Daily for anon, monthly for registered
    free_tier_reset_at: datetime | None = None
    is_free_tier: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def can_query(self) -> bool:
        if self.free_tier_remaining > 0:
            return True
        return self.credits > 0

    def consume_query(self, cost: CostBreakdown, cached: bool) -> int:
        """Consume quota for a query. Returns credits charged."""
        if cached and not self.is_free_tier:
            return 0  # Cached queries free for paid users

        if self.free_tier_remaining > 0:
            self.free_tier_remaining -= 1
            self.updated_at = utc_now()
            return 0

        credits_to_charge = cost.total_credits
        self.credits -= credits_to_charge
        self.updated_at = utc_now()
        return credits_to_charge
