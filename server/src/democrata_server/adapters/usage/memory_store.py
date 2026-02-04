from datetime import UTC, datetime, timedelta
from uuid import UUID

from polly_pipeline_server.domain.ingestion.entities import Job
from polly_pipeline_server.domain.usage.entities import UserBalance


class InMemoryJobStore:
    def __init__(self):
        self._jobs: dict[UUID, Job] = {}

    async def save(self, job: Job) -> None:
        self._jobs[job.id] = job

    async def get(self, job_id: UUID) -> Job | None:
        return self._jobs.get(job_id)


class InMemoryBalanceStore:
    def __init__(self, anon_daily_limit: int = 10):
        self._balances: dict[str, UserBalance] = {}
        self.anon_daily_limit = anon_daily_limit

    async def get_by_session(self, session_id: str) -> UserBalance | None:
        return self._balances.get(f"session:{session_id}")

    async def get_by_user(self, user_id: UUID) -> UserBalance | None:
        return self._balances.get(f"user:{user_id}")

    async def save(self, balance: UserBalance) -> None:
        if balance.user_id:
            self._balances[f"user:{balance.user_id}"] = balance
        elif balance.session_id:
            self._balances[f"session:{balance.session_id}"] = balance

    async def create_session_balance(self, session_id: str) -> UserBalance:
        balance = UserBalance(
            user_id=None,
            session_id=session_id,
            credits=0,
            free_tier_remaining=self.anon_daily_limit,
            free_tier_reset_at=datetime.now(UTC) + timedelta(days=1),
            is_free_tier=True,
        )
        await self.save(balance)
        return balance
