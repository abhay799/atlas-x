from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from atlas.domain.control import ActionDefinition, Clock, Evidence, Outcome, Reason
from atlas.domain.models import AgentIdentity


@dataclass
class TrustProfile:
    agent_id: str
    accuracy: float = 0.5
    evidence_quality: float = 0.5
    policy_compliance: float = 1.0
    tool_reliability: float = 1.0
    mission_success: float = 0.5
    security_score: float = 1.0
    version: int = 1

    @property
    def score(self) -> float:
        return max(
            0.0,
            min(
                1.0,
                sum(
                    (
                        self.accuracy,
                        self.evidence_quality,
                        self.policy_compliance,
                        self.tool_reliability,
                        self.mission_success,
                        self.security_score,
                    )
                )
                / 6,
            ),
        )


class TrustEngine:
    def __init__(self) -> None:
        self._p: dict[str, TrustProfile] = {}

    def get(self, a: str) -> TrustProfile:
        return self._p.setdefault(a, TrustProfile(a))

    def update(self, a: str, **m: float) -> TrustProfile:
        p = self.get(a)
        data = p.__dict__ | {k: max(0, min(1, v)) for k, v in m.items() if k in p.__dict__}
        data["version"] = p.version + 1
        self._p[a] = TrustProfile(**data)
        return self._p[a]


@dataclass(frozen=True)
class AuthorityGrant:
    grant_id: UUID
    agent_id: str
    level: int
    scope: str
    reason: str
    evidence: tuple[UUID, ...]
    starts_at: datetime
    expires_at: datetime
    issuer: str
    emergency: bool = False
    revoked: bool = False


class AuthorityEngine:
    def __init__(self, clock: Clock | None = None):
        self.clock = clock or Clock()
        self.grants: dict[UUID, AuthorityGrant] = {}

    def grant(
        self,
        agent_id: str,
        level: int,
        scope: str,
        reason: str,
        issuer: str,
        duration_seconds: int,
        evidence: tuple[UUID, ...] = (),
        emergency: bool = False,
    ) -> AuthorityGrant:
        now = self.clock.now()
        g = AuthorityGrant(
            uuid4(),
            agent_id,
            level,
            scope,
            reason,
            evidence,
            now,
            now + timedelta(seconds=duration_seconds),
            issuer,
            emergency,
        )
        self.grants[g.grant_id] = g
        return g

    def effective(self, agent: AgentIdentity, scope: str) -> int:
        now = self.clock.now()
        levels = [int(agent.authority)]
        levels += [
            g.level
            for g in self.grants.values()
            if g.agent_id == agent.agent_id
            and not g.revoked
            and g.starts_at <= now < g.expires_at
            and (g.scope == scope or g.scope == "*")
        ]
        return max(levels)

    def revoke(self, gid: UUID) -> None:
        g = self.grants[gid]
        self.grants[gid] = AuthorityGrant(**(g.__dict__ | {"revoked": True}))


@dataclass(frozen=True)
class Policy:
    policy_id: str
    version: str
    priority: int
    conditions: tuple[tuple[str, str, Any], ...]
    outcome: Outcome
    reason: Reason = Reason.POLICY_DENIED
    effective_from: datetime | None = None


class PolicyEngine:
    def __init__(self) -> None:
        self.policies: list[Policy] = []

    def register(self, p: Policy) -> None:
        self.policies.append(p)
        self.policies.sort(key=lambda x: x.priority, reverse=True)

    def evaluate(self, ctx: dict[str, Any]) -> tuple[Outcome | None, tuple[str, ...]]:
        for p in self.policies:
            if all(self._match(ctx.get(k), op, v) for k, op, v in p.conditions):
                return p.outcome, (f"{p.policy_id}@{p.version}",)
        return None, ()

    @staticmethod
    def _match(actual: Any, op: str, want: Any) -> bool:
        if op == "==":
            return bool(actual == want)
        if op == "!=":
            return bool(actual != want)
        if op == ">":
            return actual is not None and bool(actual > want)
        if op == ">=":
            return actual is not None and bool(actual >= want)
        if op == "in":
            return actual in want
        return False


@dataclass(frozen=True)
class Proposal:
    proposal_id: UUID
    agent_id: str
    action: str
    target: str
    confidence: float
    evidence: tuple[UUID, ...]
    objective: str


class ConflictEngine:
    OPPOSITES = {("deploy", "rollback"), ("scale_up", "scale_down"), ("isolate", "restore_traffic")}

    def conflicts(self, items: list[Proposal]) -> list[tuple[UUID, UUID]]:
        out = []
        for i, a in enumerate(items):
            for b in items[i + 1 :]:
                if a.target == b.target and (
                    (a.action, b.action) in self.OPPOSITES or (b.action, a.action) in self.OPPOSITES
                ):
                    out.append((a.proposal_id, b.proposal_id))
        return out


@dataclass(frozen=True)
class ConsensusResult:
    score: float
    independent_weight: float
    correlated: bool
    explanation: str


class ConsensusEngine:
    def assess(self, votes: list[dict[str, Any]]) -> ConsensusResult:
        if not votes:
            return ConsensusResult(0, 0, True, "no assessments")
        groups = {
            (v.get("model"), tuple(sorted(v.get("sources", ()))), v.get("parent")) for v in votes
        }
        independence = len(groups) / len(votes)
        weighted = sum(
            float(v.get("confidence", 0))
            * float(v.get("trust", 0.5))
            * float(v.get("evidence_quality", 0.5))
            for v in votes
        ) / len(votes)
        correlated = independence < 0.6
        return ConsensusResult(
            weighted,
            independence,
            correlated,
            "correlated inputs" if correlated else "sufficient source diversity",
        )


class EvidenceRegistry:
    def __init__(self) -> None:
        self.items: dict[UUID, Evidence] = {}

    def add(self, e: Evidence) -> None:
        self.items[e.evidence_id] = e

    def valid_count(self, ids: tuple[UUID, ...]) -> int:
        return sum(i in self.items for i in ids)


class ActionRegistry:
    def __init__(self) -> None:
        self.items: dict[str, ActionDefinition] = {}

    def register(self, a: ActionDefinition) -> None:
        self.items[a.action_type] = a

    def get(self, k: str) -> ActionDefinition | None:
        return self.items.get(k)
