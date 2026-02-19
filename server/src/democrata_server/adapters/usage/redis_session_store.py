import json
import os
from datetime import UTC, datetime

import redis.asyncio as redis

from democrata_server.domain.usage.entities import AnonymousSession


SESSION_KEY_PREFIX = "anonymous:session:"
SESSION_TTL_SECONDS = 25 * 60 * 60


def _session_to_dict(session: AnonymousSession) -> dict:
    return {
        "session_id": session.session_id,
        "free_tier_remaining": session.free_tier_remaining,
        "free_tier_reset_at": session.free_tier_reset_at.isoformat() if session.free_tier_reset_at else None,
        "daily_limit": session.daily_limit,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }


def _dict_to_session(data: dict) -> AnonymousSession:
    def _parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        return datetime.fromisoformat(s.replace("Z", "+00:00"))

    return AnonymousSession(
        session_id=data["session_id"],
        free_tier_remaining=data.get("free_tier_remaining", 10),
        free_tier_reset_at=_parse_dt(data.get("free_tier_reset_at")),
        daily_limit=data.get("daily_limit", 10),
        created_at=_parse_dt(data.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_dt(data.get("updated_at")) or datetime.now(UTC),
    )


class RedisAnonymousSessionStore:
    def __init__(self, url: str | None = None, daily_limit: int = 10):
        self._url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._daily_limit = daily_limit
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)
        return self._client

    def _key(self, session_id: str) -> str:
        return f"{SESSION_KEY_PREFIX}{session_id}"

    async def get(self, session_id: str) -> AnonymousSession | None:
        client = await self._get_client()
        data = await client.get(self._key(session_id))
        if data is None:
            return None
        session = _dict_to_session(json.loads(data))
        session.check_and_reset()
        return session

    async def create(self, session: AnonymousSession) -> AnonymousSession:
        client = await self._get_client()
        data = json.dumps(_session_to_dict(session))
        await client.setex(self._key(session.session_id), SESSION_TTL_SECONDS, data)
        return session

    async def update(self, session: AnonymousSession) -> AnonymousSession:
        client = await self._get_client()
        data = json.dumps(_session_to_dict(session))
        await client.setex(self._key(session.session_id), SESSION_TTL_SECONDS, data)
        return session

    async def get_or_create(self, session_id: str) -> AnonymousSession:
        session = await self.get(session_id)
        if session is None:
            session = AnonymousSession.create(session_id, self._daily_limit)
            await self.create(session)
        return session
