from typing import Protocol
from uuid import UUID

from .entities import UsageEvent, UserBalance


class UsageLogger(Protocol):
    async def log(self, event: UsageEvent) -> None:
        """Log a usage event."""
        ...


class BalanceStore(Protocol):
    async def get_by_session(self, session_id: str) -> UserBalance | None:
        """Get balance by session ID (for anonymous users)."""
        ...

    async def get_by_user(self, user_id: UUID) -> UserBalance | None:
        """Get balance by user ID (for registered users)."""
        ...

    async def save(self, balance: UserBalance) -> None:
        """Save or update balance."""
        ...

    async def create_session_balance(self, session_id: str) -> UserBalance:
        """Create a new balance for an anonymous session."""
        ...
