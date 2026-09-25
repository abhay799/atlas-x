from uuid import UUID

from atlas.capabilities.service import CapabilityRegistry
from atlas.domain.models import AgentIdentity, DecisionOutcome, GovernanceDecision, MissionTask
from atlas.governance.constitution import AtlasConstitution


class DecisionGateway:
    def __init__(self, constitution: AtlasConstitution, capabilities: CapabilityRegistry) -> None:
        self.constitution = constitution
        self.capabilities = capabilities

    def evaluate(
        self, agent: AgentIdentity | None, task: MissionTask, mission_id: UUID | None = None
    ) -> GovernanceDecision:
        reasons: list[str] = []
        if agent is None or not agent.is_valid_now():
            reasons.append("missing_or_invalid_agent_identity")
        else:
            missing = [
                c
                for c in task.required_capabilities
                if not self.capabilities.has(agent.agent_id, c)
            ]
            if missing:
                reasons.append(f"missing_capabilities:{','.join(sorted(missing))}")
            if agent.authority < task.authority_required:
                reasons.append("insufficient_authority")
            if (
                self.constitution.evidence_required_for_governed_actions
                and not task.evidence_requirements
            ):
                reasons.append("missing_evidence_requirements")
        outcome = DecisionOutcome.BLOCK if reasons else DecisionOutcome.ALLOW
        return GovernanceDecision(
            outcome=outcome,
            reasons=tuple(reasons or ["foundational_checks_passed"]),
            mission_id=mission_id,
            agent_id=agent.agent_id if agent else None,
            constitution_version=self.constitution.constitution_version,
        )
