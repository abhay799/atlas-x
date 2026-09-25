from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from atlas.domain.models import AgentIdentity
from atlas.governance.engines import TrustEngine


class TeamState(StrEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    DISSOLVED = "DISSOLVED"


@dataclass
class Team:
    team_id: UUID
    mission_id: UUID
    agents: list[str]
    state: TeamState = TeamState.CREATED


class TeamFormation:
    def __init__(self, trust: TrustEngine):
        self.trust = trust

    def form(self, mission_id: UUID, required: set[str], agents: list[AgentIdentity]) -> Team:
        eligible = [
            a for a in agents if a.is_valid_now() and required.issubset(a.declared_capabilities)
        ]
        eligible.sort(
            key=lambda a: (int(a.authority), self.trust.get(a.agent_id).score), reverse=True
        )
        if not eligible:
            raise ValueError("no eligible agent team")
        return Team(uuid4(), mission_id, [eligible[0].agent_id])
