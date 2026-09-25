from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from uuid import UUID


@dataclass(frozen=True)
class ConsumedAuthorization:
    authorization_id: UUID
    correlation_id: UUID
    consumed_at: datetime


class ExecutionAuthorizationStore:
    """Thread-safe, process-local single-use authorization registry."""

    def __init__(self) -> None:
        self._consumed: dict[UUID, ConsumedAuthorization] = {}
        self._lock = Lock()

    def consume(self, authorization_id: UUID, correlation_id: UUID) -> ConsumedAuthorization:
        with self._lock:
            if authorization_id in self._consumed:
                raise PermissionError("execution authorization has already been consumed")
            consumed = ConsumedAuthorization(authorization_id, correlation_id, datetime.now(UTC))
            self._consumed[authorization_id] = consumed
            return consumed

    def consumed(self, authorization_id: UUID) -> ConsumedAuthorization | None:
        with self._lock:
            return self._consumed.get(authorization_id)
