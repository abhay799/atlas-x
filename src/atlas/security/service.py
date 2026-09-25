from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ContentAssessment:
    untrusted: bool
    prompt_injection: bool
    reasons: tuple[str, ...]


class ContentDefense:
    TOKENS = (
        "ignore previous",
        "system prompt",
        "send credentials",
        "bypass policy",
        "grant yourself",
        "disable audit",
    )

    def inspect(self, text: str) -> ContentAssessment:
        hits = tuple(t for t in self.TOKENS if t in text.lower())
        return ContentAssessment(True, bool(hits), hits)


class AnomalyDetector:
    def score(self, baseline: set[str], requested: set[str], frequency_ratio: float = 1.0) -> float:
        return min(
            1.0,
            0.7 * (len(requested - baseline) / max(1, len(requested)))
            + 0.3 * max(0.0, min(1.0, (frequency_ratio - 1) / 4)),
        )


@dataclass
class QuarantineRecord:
    record_id: UUID
    agent_id: str
    reason: str
    active: bool
    created_at: datetime
    snapshot: dict[str, object]


class Quarantine:
    def __init__(self) -> None:
        self.records: dict[str, QuarantineRecord] = {}

    def quarantine(self, a: str, reason: str, snapshot: dict[str, object]) -> QuarantineRecord:
        r = QuarantineRecord(uuid4(), a, reason, True, datetime.now(UTC), snapshot)
        self.records[a] = r
        return r

    def release(self, a: str) -> None:
        if a in self.records:
            self.records[a].active = False

    def active(self, a: str) -> bool:
        return a in self.records and self.records[a].active
