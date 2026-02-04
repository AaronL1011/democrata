"""Domain entities for the agent pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QueryType(str, Enum):
    """Classification of query intent."""

    FACTUAL = "factual"  # Simple fact lookup
    COMPARATIVE = "comparative"  # Comparing entities (parties, policies)
    TIMELINE = "timeline"  # Chronological events
    VOTING = "voting"  # Parliamentary vote information
    ANALYTICAL = "analytical"  # Analysis or explanation


class RetrievalStrategy(str, Enum):
    """Strategy for context retrieval based on query type."""

    SINGLE_FOCUS = "single_focus"  # Single embedding search
    MULTI_ENTITY = "multi_entity"  # Parallel searches per entity
    CHRONOLOGICAL = "chronological"  # Date-filtered, time-ordered
    BROAD = "broad"  # Wider search with diversity sampling


class ResponseDepth(str, Enum):
    """Depth of response based on query complexity."""

    BRIEF = "brief"  # Simple factual queries, 1-2 sections
    STANDARD = "standard"  # Comparative/timeline queries, 2-4 sections
    COMPREHENSIVE = "comprehensive"  # Analytical queries, 4-8 sections


@dataclass
class ExtractedEntities:
    """Entities extracted from a user query."""

    parties: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    bills: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    date_from: str | None = None
    date_to: str | None = None
    document_types: list[str] = field(default_factory=list)

    def has_entities(self) -> bool:
        """Check if any entities were extracted."""
        return bool(
            self.parties
            or self.members
            or self.bills
            or self.topics
            or self.document_types
        )


@dataclass
class IntentResult:
    """Result of query intent classification."""

    query_type: QueryType
    entities: ExtractedEntities
    expected_components: list[str]
    retrieval_strategy: RetrievalStrategy
    rewritten_queries: list[str] = field(default_factory=list)
    confidence: float = 1.0
    response_depth: ResponseDepth = ResponseDepth.STANDARD

    @classmethod
    def default_factual(cls, query: str) -> "IntentResult":
        """Create a default factual intent when classification fails."""
        return cls(
            query_type=QueryType.FACTUAL,
            entities=ExtractedEntities(),
            expected_components=["text_block"],
            retrieval_strategy=RetrievalStrategy.SINGLE_FOCUS,
            rewritten_queries=[query],
            confidence=0.5,
            response_depth=ResponseDepth.BRIEF,
        )


@dataclass
class SourceQuote:
    """A quote from source context with attribution."""

    text: str
    chunk_index: int | None = None
    document_id: str | None = None


@dataclass
class ExtractionResult:
    """Result of grounded data extraction for a single component."""

    component_type: str
    extracted_data: dict[str, Any]
    source_quotes: list[SourceQuote] = field(default_factory=list)
    completeness: float = 1.0  # 0-1, how much data was extractable
    warnings: list[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Check if extraction has sufficient data."""
        return self.completeness >= 0.5 and bool(self.extracted_data)

    @classmethod
    def empty(cls, component_type: str, reason: str) -> "ExtractionResult":
        """Create an empty extraction result."""
        return cls(
            component_type=component_type,
            extracted_data={},
            completeness=0.0,
            warnings=[reason],
        )


@dataclass
class UnsupportedClaim:
    """A claim in the response not supported by context."""

    claim_text: str
    component_id: str | None = None
    severity: str = "warning"  # warning, error


@dataclass
class VerificationResult:
    """Result of response verification against source context."""

    is_valid: bool
    unsupported_claims: list[UnsupportedClaim] = field(default_factory=list)
    confidence_score: float = 1.0
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def valid(cls) -> "VerificationResult":
        """Create a valid verification result."""
        return cls(is_valid=True, confidence_score=1.0)

    @classmethod
    def invalid(cls, claims: list[UnsupportedClaim]) -> "VerificationResult":
        """Create an invalid verification result."""
        return cls(
            is_valid=False,
            unsupported_claims=claims,
            confidence_score=0.0,
        )
