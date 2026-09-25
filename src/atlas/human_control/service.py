from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from atlas.observability import Telemetry


class HumanAction(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    RESTRICT = "RESTRICT"
    TAKE_CONTROL = "TAKE_CONTROL"
    STOP = "STOP"


@dataclass(frozen=True)
class HumanDecision:
    event_id: UUID
    mission_id: UUID
    actor: str
    action: HumanAction
    reason: str
    timestamp: datetime


class HumanControl:
    def __init__(self, telemetry: Telemetry | None = None) -> None:
        self.events: list[HumanDecision] = []
        self.telemetry = telemetry

    def record(
        self, mission_id: UUID, actor: str, action: HumanAction, reason: str
    ) -> HumanDecision:
        e = HumanDecision(uuid4(), mission_id, actor, action, reason, datetime.now(UTC))
        self.events.append(e)
        if self.telemetry is not None:
            if action == HumanAction.APPROVE:
                self.telemetry.increment("human_approvals_total")
                outcome = "approved"
            elif action in {HumanAction.REJECT, HumanAction.STOP}:
                self.telemetry.increment("human_rejections_total")
                outcome = "rejected"
            else:
                outcome = "recorded"
            self.telemetry.emit(
                "human.decision",
                mission_id=str(mission_id),
                agent_id=actor,
                action=action.value,
                outcome=outcome,
            )
        return e

    def rejected(self, mission_id: UUID) -> bool:
        return any(
            e.mission_id == mission_id and e.action in {HumanAction.REJECT, HumanAction.STOP}
            for e in self.events
        )

    def approved(self, mission_id: UUID) -> bool:
        return any(
            e.mission_id == mission_id and e.action == HumanAction.APPROVE for e in self.events
        )


class EmergencyBrake:
    def __init__(self) -> None:
        self.fabric = False
        self.agents: set[str] = set()
        self.missions: set[UUID] = set()
        self.capabilities: set[str] = set()
        self.environments: set[str] = set()

    def stop_fabric(self) -> None:
        self.fabric = True

    def stop_agent(self, a: str) -> None:
        self.agents.add(a)

    def stop_mission(self, m: UUID) -> None:
        self.missions.add(m)

    def disable_capability(self, c: str) -> None:
        self.capabilities.add(c)

    def isolate_environment(self, e: str) -> None:
        self.environments.add(e)

    def blocked(
        self,
        agent: str,
        mission: UUID,
        capability: str | None = None,
        environment: str | None = None,
    ) -> bool:
        return (
            self.fabric
            or agent in self.agents
            or mission in self.missions
            or (capability in self.capabilities if capability else False)
            or (environment in self.environments if environment else False)
        )
