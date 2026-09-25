from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Outcome(StrEnum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    DELAY = "DELAY"
    MODIFY = "MODIFY"
    QUARANTINE = "QUARANTINE"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class Reason(StrEnum):
    IDENTITY_INVALID = "IDENTITY_INVALID"
    CAPABILITY_MISSING = "CAPABILITY_MISSING"
    AUTHORITY_INSUFFICIENT = "AUTHORITY_INSUFFICIENT"
    POLICY_DENIED = "POLICY_DENIED"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    RISK_BUDGET_EXCEEDED = "RISK_BUDGET_EXCEEDED"
    BLAST_RADIUS_HIGH = "BLAST_RADIUS_HIGH"
    ACTION_IRREVERSIBLE = "ACTION_IRREVERSIBLE"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    AGENT_QUARANTINED = "AGENT_QUARANTINED"
    EMERGENCY_STOP_ACTIVE = "EMERGENCY_STOP_ACTIVE"
    CONTEXT_UNSAFE = "CONTEXT_UNSAFE"
    CONFLICT_UNRESOLVED = "CONFLICT_UNRESOLVED"
    CONSENSUS_CORRELATED = "CONSENSUS_CORRELATED"
    RED_TEAM_FAILED = "RED_TEAM_FAILED"
    SIMULATION_FAILED = "SIMULATION_FAILED"
    HARD_POLICY = "HARD_POLICY"


class GovState(StrEnum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    QUARANTINED = "QUARANTINED"
    STOPPED = "STOPPED"
    ROLLED_BACK = "ROLLED_BACK"


TRANSITIONS = {
    GovState.PROPOSED: {GovState.UNDER_REVIEW, GovState.BLOCKED},
    GovState.UNDER_REVIEW: {
        GovState.APPROVAL_REQUIRED,
        GovState.AUTHORIZED,
        GovState.BLOCKED,
        GovState.QUARANTINED,
        GovState.STOPPED,
    },
    GovState.APPROVAL_REQUIRED: {GovState.AUTHORIZED, GovState.BLOCKED, GovState.STOPPED},
    GovState.AUTHORIZED: {GovState.EXECUTING, GovState.STOPPED},
    GovState.EXECUTING: {
        GovState.VERIFYING,
        GovState.FAILED,
        GovState.STOPPED,
        GovState.ROLLED_BACK,
    },
    GovState.VERIFYING: {GovState.COMPLETED, GovState.FAILED, GovState.ROLLED_BACK},
}


def transition(current: GovState, target: GovState) -> GovState:
    if target not in TRANSITIONS.get(current, set()):
        raise ValueError(f"illegal governance transition {current}->{target}")
    return target


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    evidence_id: UUID = Field(default_factory=uuid4)
    source: str
    content_hash: str = Field(min_length=8)
    provenance: str
    confidence: float = Field(ge=0, le=1)
    freshness_seconds: int = Field(ge=0)
    owner: str
    trust_boundary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActionDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)
    action_type: str
    required_capabilities: frozenset[str] = frozenset()
    minimum_authority: int = Field(ge=0, le=5)
    reversibility: float = Field(ge=0, le=1)
    default_risk: float = Field(ge=0, le=100)
    required_evidence: int = Field(ge=0)
    human_approval_if: tuple[str, ...] = ()
    adapter: str = "simulation"


class GovernanceDecisionV2(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    agent_id: str
    outcome: Outcome
    reason_codes: tuple[Reason, ...]
    evidence_refs: tuple[UUID, ...] = ()
    policy_refs: tuple[str, ...] = ()
    authority_context: dict[str, Any] = Field(default_factory=dict)
    risk_assessment: dict[str, Any] = Field(default_factory=dict)
    reversibility_assessment: dict[str, Any] = Field(default_factory=dict)
    blast_radius_assessment: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    constitution_version: str
    provenance_ref: UUID = Field(default_factory=uuid4)


class Clock:
    def now(self) -> datetime:
        return datetime.now(UTC)
