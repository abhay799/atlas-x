from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any
from uuid import UUID, uuid4

from atlas.domain.control import Outcome


@dataclass(frozen=True)
class RedTeamFinding:
    code: str
    severity: str
    detail: str


class RedTeam:
    def review(self, ctx: dict[str, Any]) -> list[RedTeamFinding]:
        f = []
        if ctx.get("evidence_count", 0) < ctx.get("required_evidence", 0):
            f.append(RedTeamFinding("missing_evidence", "high", "required evidence absent"))
        if ctx.get("prompt_injection"):
            f.append(
                RedTeamFinding(
                    "prompt_injection",
                    "critical",
                    "untrusted content contains authority manipulation",
                )
            )
        if ctx.get("reversibility", 1) < 0.3 and not ctx.get("rollback"):
            f.append(
                RedTeamFinding("rollback_missing", "high", "low reversibility without rollback")
            )
        return f


@dataclass(frozen=True)
class BlastAssessment:
    impacted: tuple[str, ...]
    score: float


class BlastRadius:
    def __init__(self) -> None:
        self.edges: dict[str, set[str]] = {}

    def link(self, a: str, b: str) -> None:
        self.edges.setdefault(a, set()).add(b)

    def assess(self, target: str) -> BlastAssessment:
        seen = set()
        q = [target]
        while q:
            n = q.pop(0)
            for x in self.edges.get(n, set()):
                if x not in seen:
                    seen.add(x)
                    q.append(x)
        return BlastAssessment(tuple(sorted(seen)), min(100.0, len(seen) * 20.0))


@dataclass(frozen=True)
class ReversibilityAssessment:
    score: float
    classification: str


class Reversibility:
    def assess(
        self, rollback: bool, data_loss: float, external: float, recovery_confidence: float
    ) -> ReversibilityAssessment:
        s = max(
            0.0,
            min(
                1.0,
                (0.4 if rollback else 0)
                + 0.3 * recovery_confidence
                + 0.15 * (1 - data_loss)
                + 0.15 * (1 - external),
            ),
        )
        c = "high" if s >= 0.75 else "medium" if s >= 0.4 else "low"
        return ReversibilityAssessment(s, c)


class RiskBudget:
    def __init__(self, total: float) -> None:
        self.total = total
        self.consumed = 0.0
        self.reserved: dict[UUID, float] = {}
        self._lock = RLock()

    @property
    def remaining(self) -> float:
        with self._lock:
            return self.total - self.consumed - sum(self.reserved.values())

    def reserve(self, amount: float) -> UUID:
        with self._lock:
            if amount < 0 or amount > self.remaining:
                raise ValueError("risk budget exceeded")
            k = uuid4()
            self.reserved[k] = amount
            return k

    def commit(self, k: UUID) -> None:
        with self._lock:
            self.consumed += self.reserved.pop(k)

    def release(self, k: UUID) -> None:
        with self._lock:
            self.reserved.pop(k, None)


class Counterfactual:
    def evaluate(self, models: dict[Outcome, dict[str, Any]]) -> dict[Outcome, dict[str, Any]]:
        return models.copy()
