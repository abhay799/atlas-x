from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    event_id: UUID = Field(default_factory=uuid4)
    correlation_id: UUID
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    mission_id: UUID | None = None
    agent_id: str | None = None
    decision_id: UUID | None = None
    constitution_version: str
    payload: dict[str, Any] = Field(default_factory=dict)


class InMemoryAuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
