from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from atlas.domain.control import Clock


@dataclass(frozen=True)
class Delegation:
    delegation_id: UUID
    organization: str
    agent_id: str
    capabilities: frozenset[str]
    scope: str
    expires_at: datetime
    revoked: bool = False


class Federation:
    def __init__(self, clock: Clock | None = None):
        self.clock = clock or Clock()
        self.delegations: dict[UUID, Delegation] = {}

    def add(self, d: Delegation) -> None:
        self.delegations[d.delegation_id] = d

    def valid(self, did: UUID, cap: str) -> bool:
        d = self.delegations[did]
        return not d.revoked and self.clock.now() < d.expires_at and cap in d.capabilities
