from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4


class CandidateState(StrEnum):
    CANDIDATE = "candidate"
    REPLAYED = "replayed"
    SIMULATED = "simulated"
    SHADOW = "shadow"
    HUMAN_REVIEW = "human_review"
    PROMOTED = "promoted"


@dataclass
class GovernanceCandidate:
    candidate_id: UUID
    description: str
    state: CandidateState = CandidateState.CANDIDATE
    human_approved: bool = False


class LearningEngine:
    def propose(self, d: str) -> GovernanceCandidate:
        return GovernanceCandidate(uuid4(), d)

    def advance(self, c: GovernanceCandidate, target: CandidateState) -> None:
        order = list(CandidateState)
        cur = order.index(c.state)
        nxt = order.index(target)
        if nxt != cur + 1:
            raise ValueError("candidate pipeline must advance one stage")
        if target == CandidateState.PROMOTED and not c.human_approved:
            raise ValueError("human approval required for promotion")
        c.state = target
