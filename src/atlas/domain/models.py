from __future__ import annotations

from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthorityLevel(IntEnum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5


class AgentStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class TaskStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class MissionStatus(StrEnum):
    COMPILED = "compiled"
    READY = "ready"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class DecisionOutcome(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    BLOCK = "BLOCK"


class Capability(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str = Field(min_length=2, pattern=r"^[a-z][a-z0-9_.:-]+$")
    scope: str = Field(default="global", min_length=1)
    restrictions: tuple[str, ...] = ()
    version: str = "1.0"
    provenance: str = "declared"


class AgentIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)
    agent_id: str = Field(min_length=3, pattern=r"^[a-z0-9][a-z0-9-]{2,63}$")
    role: str = Field(min_length=2)
    authority: AuthorityLevel
    status: AgentStatus = AgentStatus.ACTIVE
    declared_capabilities: frozenset[str] = frozenset()
    allowed_actions: frozenset[str] = frozenset()
    forbidden_actions: frozenset[str] = frozenset()
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    identity_provenance: str = Field(min_length=2)
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    @field_validator("forbidden_actions")
    @classmethod
    def no_action_overlap(cls, value: frozenset[str], info: Any) -> frozenset[str]:
        allowed = info.data.get("allowed_actions", frozenset())
        if value & allowed:
            raise ValueError("an action cannot be both allowed and forbidden")
        return value

    def is_valid_now(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return self.status == AgentStatus.ACTIVE and (
            self.expires_at is None or self.expires_at > current
        )


class MissionTask(BaseModel):
    model_config = ConfigDict(frozen=True)
    task_id: str
    title: str
    dependencies: tuple[str, ...] = ()
    required_capabilities: frozenset[str] = frozenset()
    authority_required: AuthorityLevel = AuthorityLevel.L1
    evidence_requirements: tuple[str, ...] = ()
    assigned_agent_id: str | None = None
    status: TaskStatus = TaskStatus.PENDING


class Mission(BaseModel):
    mission_id: UUID = Field(default_factory=uuid4)
    objective: str = Field(min_length=5)
    constraints: tuple[str, ...] = ()
    tasks: tuple[MissionTask, ...]
    authority_ceiling: AuthorityLevel = AuthorityLevel.L3
    execution_restrictions: tuple[str, ...] = ("no_direct_execution",)
    human_approval_required: bool = False
    status: MissionStatus = MissionStatus.COMPILED
    constitution_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str = "human"


class GovernanceDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    outcome: DecisionOutcome
    reasons: tuple[str, ...]
    mission_id: UUID | None = None
    agent_id: str | None = None
    constitution_version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
