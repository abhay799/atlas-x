from uuid import UUID, uuid4

from atlas.capabilities.service import CapabilityRegistry
from atlas.domain.models import AgentIdentity, Capability, GovernanceDecision, Mission
from atlas.governance.constitution import AtlasConstitution
from atlas.governance.gateway import DecisionGateway
from atlas.identity.service import AgentRegistry
from atlas.missions.compiler import DeterministicMissionCompiler
from atlas.missions.graph import MissionGraph
from atlas.observability import Telemetry
from atlas.provenance.audit import AuditEvent, InMemoryAuditLog


class AtlasService:
    def __init__(self, constitution: AtlasConstitution, telemetry: Telemetry | None = None) -> None:
        self.constitution = constitution
        self.agents = AgentRegistry()
        self.capabilities = CapabilityRegistry()
        self.compiler = DeterministicMissionCompiler()
        self.audit = InMemoryAuditLog()
        self._missions: dict[UUID, Mission] = {}
        self.gateway = DecisionGateway(constitution, self.capabilities)
        self.telemetry = telemetry or Telemetry()

    def register_agent(self, agent: AgentIdentity) -> AgentIdentity:
        result = self.agents.register(agent)
        for cap in agent.declared_capabilities:
            if self.capabilities.is_registered(cap):
                self.capabilities.grant_declared(agent.agent_id, cap)
        return result

    def register_capability(self, capability: Capability) -> Capability:
        return self.capabilities.register_capability(capability)

    def grant_capability(self, agent_id: str, capability_name: str) -> None:
        agent = self.agents.get(agent_id)
        if agent is None or capability_name not in agent.declared_capabilities:
            raise ValueError("capability was not declared by agent identity")
        self.capabilities.grant_declared(agent_id, capability_name)

    def compile_mission(self, objective: str, constraints: tuple[str, ...]) -> Mission:
        mission = self.compiler.compile(
            objective, constraints, self.constitution.constitution_version
        )
        MissionGraph(mission)
        self._missions[mission.mission_id] = mission
        self.telemetry.emit("mission.created", mission_id=str(mission.mission_id))
        return mission

    def get_mission(self, mission_id: UUID) -> Mission | None:
        return self._missions.get(mission_id)

    def evaluate(
        self,
        mission_id: UUID,
        task_id: str,
        agent_id: str | None,
        correlation_id: UUID | None = None,
    ) -> GovernanceDecision:
        mission = self._missions.get(mission_id)
        if mission is None:
            raise ValueError("mission not found")
        task = MissionGraph(mission).task(task_id)
        agent = self.agents.get(agent_id) if agent_id else None
        decision = self.gateway.evaluate(agent, task, mission_id)
        self.audit.append(
            AuditEvent(
                correlation_id=correlation_id or uuid4(),
                event_type="governance.decision",
                mission_id=mission_id,
                agent_id=agent_id,
                decision_id=decision.decision_id,
                constitution_version=self.constitution.constitution_version,
                payload={
                    "outcome": decision.outcome.value,
                    "reasons": list(decision.reasons),
                    "required_capabilities": sorted(task.required_capabilities),
                },
            )
        )
        self.telemetry.increment("governance_decisions_total")
        self.telemetry.increment(f"governance_{decision.outcome.value.lower()}_total")
        outcome_metric = {
            "ALLOW": "governance_allow_total",
            "BLOCK": "governance_block_total",
            "REQUIRE_HUMAN_APPROVAL": "governance_approval_required_total",
        }.get(decision.outcome.value)
        if outcome_metric is not None:
            self.telemetry.increment(outcome_metric)
        self.telemetry.emit(
            "agent.evaluated",
            correlation_id=str(correlation_id) if correlation_id else None,
            decision_id=str(decision.decision_id),
            mission_id=str(mission_id),
            agent_id=agent_id,
            outcome=decision.outcome.value,
            reason_codes=",".join(decision.reasons),
        )
        return decision
