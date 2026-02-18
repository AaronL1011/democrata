from dataclasses import fields, is_dataclass
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from democrata_server.api.http.deps import (
    AnonymousBillingContext,
    UserBillingContext,
    get_anonymous_session_store,
    get_billing_account_repository,
    get_execute_query_use_case,
    get_rag_billing_context,
    get_session_id,
    get_transaction_repository,
    get_usage_event_repository,
)
from democrata_server.domain.billing.entities import (
    CreditTransaction,
    ESTIMATED_MAX_QUERY_CREDITS,
)
from democrata_server.domain.rag.entities import Query, QueryFilters
from democrata_server.domain.rag.use_cases import ExecuteQuery
from democrata_server.domain.usage.entities import UsageEvent

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    filters: dict | None = None


class ComponentData(BaseModel):
    id: str
    type: str
    data: dict
    size: str | None = None


class SectionData(BaseModel):
    title: str | None = None
    component_ids: list[str]
    layout: str | None = None


class LayoutData(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    sections: list[SectionData]


class CostBreakdownData(BaseModel):
    embedding_tokens: int
    llm_input_tokens: int
    llm_output_tokens: int
    total_cents: int
    total_credits: int


class QueryMetadataData(BaseModel):
    documents_retrieved: int
    chunks_used: int
    processing_time_ms: int
    model: str


class SourceReferenceData(BaseModel):
    document_id: str
    source_name: str
    source_url: str | None = None
    source_date: str | None = None


class QueryResponse(BaseModel):
    layout: LayoutData
    components: list[ComponentData]
    cost: CostBreakdownData
    cached: bool
    metadata: QueryMetadataData
    sources: list[SourceReferenceData]
    credits_charged: int = 0
    balance_remaining: int | None = None


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    session_id: str = Depends(get_session_id),
    billing_context: UserBillingContext | AnonymousBillingContext = Depends(get_rag_billing_context),
    execute_query: ExecuteQuery = Depends(get_execute_query_use_case),
    billing_repo=Depends(get_billing_account_repository),
    usage_event_repo=Depends(get_usage_event_repository),
    transaction_repo=Depends(get_transaction_repository),
    anonymous_store=Depends(get_anonymous_session_store),
) -> QueryResponse:
    filters = None
    if request.filters:
        filters = QueryFilters(
            document_types=request.filters.get("document_types"),
            date_from=request.filters.get("date_from"),
            date_to=request.filters.get("date_to"),
            sources=request.filters.get("sources"),
            member_ids=request.filters.get("member_ids"),
        )

    if isinstance(billing_context, AnonymousBillingContext):
        if not billing_context.session.can_query():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Free daily limit reached. Sign in for 100/month or add credits.",
            )
    else:
        account = billing_context.account
        if account.can_consume(1):
            pass
        elif not account.can_consume(ESTIMATED_MAX_QUERY_CREDITS):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits. Add credits to continue.",
            )

    query_obj = Query(
        text=request.query,
        session_id=session_id,
        filters=filters,
    )

    try:
        result = await execute_query.execute(query_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    credits_charged = 0
    balance_remaining = None

    if isinstance(billing_context, AnonymousBillingContext):
        billing_context.session.consume_query()
        await anonymous_store.update(billing_context.session)
    else:
        account = billing_context.account
        cached = result.result.cached
        on_free_tier = account.free_tier_remaining > 0
        if cached:
            if on_free_tier:
                account.consume(1, use_free_tier_first=True)
            credits_charged = 0
        else:
            if on_free_tier:
                account.consume(1, use_free_tier_first=True)
                credits_charged = 0
            else:
                credits_to_charge = result.cost.total_credits
                try:
                    paid_credits_used = account.consume(
                        credits_to_charge, use_free_tier_first=True
                    )
                    credits_charged = paid_credits_used
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="Insufficient credits for this query. Add credits to continue.",
                    )
        balance_remaining = account.credits
        await billing_repo.update(account)

        usage_event = UsageEvent.create_query_event(
            billing_account_id=account.id,
            query=request.query,
            cost=result.cost,
            cached=cached,
            user_id=billing_context.user.id,
            session_id=session_id,
            credits_charged=credits_charged,
        )
        await usage_event_repo.create(usage_event)

        if credits_charged > 0:
            transaction = CreditTransaction.create_usage(
                billing_account_id=account.id,
                amount=credits_charged,
                balance_after=account.credits,
                usage_event_id=usage_event.id,
                query_preview=usage_event.query_preview,
            )
            await transaction_repo.create(transaction)

    # Convert domain objects to response format
    components_data = []
    for comp in result.result.components:
        comp_type = type(comp.content).__name__.lower()
        comp_dict = {
            "id": comp.id,
            "type": comp_type,
            "data": _serialize_component(comp.content),
            "size": comp.size,
        }
        components_data.append(ComponentData(**comp_dict))

    sections_data = [
        SectionData(title=s.title, component_ids=s.component_ids, layout=s.layout)
        for s in result.result.layout.sections
    ]

    layout_data = LayoutData(
        title=result.result.layout.title,
        subtitle=result.result.layout.subtitle,
        sections=sections_data,
    )

    cost_data = CostBreakdownData(
        embedding_tokens=result.cost.embedding_tokens,
        llm_input_tokens=result.cost.llm_input_tokens,
        llm_output_tokens=result.cost.llm_output_tokens,
        total_cents=result.cost.total_cents,
        total_credits=result.cost.total_credits,
    )

    metadata_data = QueryMetadataData(
        documents_retrieved=result.result.metadata.documents_retrieved,
        chunks_used=result.result.metadata.chunks_used,
        processing_time_ms=result.result.metadata.processing_time_ms,
        model=result.result.metadata.model,
    )

    sources_data = [
        SourceReferenceData(
            document_id=s.document_id,
            source_name=s.source_name,
            source_url=s.source_url,
            source_date=s.source_date,
        )
        for s in result.result.sources
    ]

    return QueryResponse(
        layout=layout_data,
        components=components_data,
        cost=cost_data,
        cached=result.result.cached,
        metadata=metadata_data,
        sources=sources_data,
        credits_charged=credits_charged,
        balance_remaining=balance_remaining,
    )


def _serialize_component(content) -> dict:
    if is_dataclass(content):
        result = {}
        for f in fields(content):
            value = getattr(content, f.name)
            result[f.name] = _serialize_value(value)
        return result
    return {"value": content}


def _serialize_value(value):
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if is_dataclass(value):
        result = {}
        for f in fields(value):
            result[f.name] = _serialize_value(getattr(value, f.name))
        return result
    return str(value)
