"""Verification-code storage adapters used by local and hosted deployments."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Optional, Protocol


class VerificationCodeStore(Protocol):
    """The small storage interface required by verification flows."""

    def get(self, key: str) -> Optional[str]: ...

    def setex(self, key: str, ttl_seconds: int, value: str) -> None: ...

    def delete(self, key: str) -> None: ...


@dataclass(frozen=True)
class _Entry:
    value: str
    expires_at: float


class InMemoryVerificationCodeStore:
    """Process-local TTL store for development without Redis."""

    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= monotonic():
                self._entries.pop(key, None)
                return None
            return entry.value

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        with self._lock:
            self._entries[key] = _Entry(
                value=str(value),
                expires_at=monotonic() + ttl_seconds,
            )

    def delete(self, key: str) -> None:
        with self._lock:
            self._entries.pop(key, None)


memory_verification_store = InMemoryVerificationCodeStore()
