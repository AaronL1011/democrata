import hashlib
import os
from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple auth middleware for API key validation on protected routes."""

    def __init__(self, app, protected_prefixes: list[str] | None = None):
        super().__init__(app)
        self.protected_prefixes = protected_prefixes or ["/ingestion"]
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> set[str]:
        keys_str = os.getenv("API_KEYS", "")
        if not keys_str:
            return set()
        return {self._hash_key(k.strip()) for k in keys_str.split(",") if k.strip()}

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        is_protected = any(path.startswith(prefix) for prefix in self.protected_prefixes)

        if is_protected and self.api_keys:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing API key")

            provided_key = auth_header[7:]
            hashed = self._hash_key(provided_key)

            if hashed not in self.api_keys:
                raise HTTPException(status_code=403, detail="Invalid API key")

        return await call_next(request)
