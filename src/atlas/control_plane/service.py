from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from atlas.domain.control import Clock, GovernanceDecisionV2, Outcome, Reason
from atlas.domain.models import AgentIdentity
from atlas.governance.engines import (
    ActionRegistry,
    AuthorityEngine,
    ConsensusEngine,
    EvidenceRegistry,
    PolicyEngine,
    TrustEngine,
)
from atlas.human_control.service import EmergencyBrake, HumanControl
from atlas.observability import Telemetry
from atlas.safety.engines import BlastRadius, RedTeam, Reversibility, RiskBudget
from atlas.security.service import Quarantine


class SupremeControlPlane:
    def __init__(self, constitution_version: str, telemetry: Telemetry | None = None) -> None:
        self.version = constitution_version
        self.clock = Clock()
        self.trust = TrustEngine()
        self.authority = AuthorityEngine(self.clock)
        self.policies = PolicyEngine()
        self.evidence = EvidenceRegistry()
        self.actions = ActionRegistry()
        self.consensus = ConsensusEngine()
        self.redteam = RedTeam()
        self.blast = BlastRadius()
        self.reversibility = Reversibility()
        self.telemetry = telemetry or Telemetry()
        self.human = HumanControl(self.telemetry)
        self.emergency = EmergencyBrake()
        self.quarantine = Quarantine()
        self.budgets: dict[UUID, RiskBudget] = {}

    def evaluate(
        self,
        mission_id: UUID,
        agent: AgentIdentity | None,
        action_type: str,
        target: str,
        context: dict[str, Any],
        evidence_ids: tuple[UUID, ...] = (),
    ) -> GovernanceDecisionV2:
        started_at = perf_counter()
        reasons = []
        policies: tuple[str, ...] = ()
        outcome = Outcome.ALLOW
        aid = agent.agent_id if agent else "unknown"
        action = self.actions.get(action_type)
        if agent is None or not agent.is_valid_now():
            reasons.append(Reason.IDENTITY_INVALID)
        if agent and self.quarantine.active(agent.agent_id):
            reasons.append(Reason.AGENT_QUARANTINED)
        if self.emergency.blocked(aid, mission_id, action_type, context.get("environment")):
            reasons.append(Reason.EMERGENCY_STOP_ACTIVE)
        if action is None:
            reasons.append(Reason.POLICY_DENIED)
        if action and agent:
            if not action.required_capabilities.issubset(agent.declared_capabilities):
                reasons.append(Reason.CAPABILITY_MISSING)
            effective = self.authority.effective(agent, target)
            if effective < action.minimum_authority:
                reasons.append(Reason.AUTHORITY_INSUFFICIENT)
            if self.evidence.valid_count(evidence_ids) < action.required_evidence:
                reasons.append(Reason.EVIDENCE_INSUFFICIENT)
        po, policies = self.policies.evaluate(context | {"action": action_type, "target": target})
        if po == Outcome.BLOCK:
            reasons.extend([Reason.POLICY_DENIED, Reason.HARD_POLICY])
        rev = self.reversibility.assess(
            bool(context.get("rollback")),
            float(context.get("data_loss_risk", 0)),
            float(context.get("external_impact", 0)),
            float(context.get("recovery_confidence", 1)),
        )
        blast = self.blast.assess(target)
        if blast.score >= 60:
            reasons.append(Reason.BLAST_RADIUS_HIGH)
        if rev.score < 0.3:
            reasons.append(Reason.ACTION_IRREVERSIBLE)
        rt = self.redteam.review(
            {
                "evidence_count": self.evidence.valid_count(evidence_ids),
                "required_evidence": action.required_evidence if action else 1,
                "prompt_injection": context.get("prompt_injection", False),
                "reversibility": rev.score,
                "rollback": context.get("rollback"),
            }
        )
        if any(f.severity == "critical" for f in rt):
            reasons.append(Reason.RED_TEAM_FAILED)
        budget = self.budgets.get(mission_id)
        risk = (
            float(action.default_risk if action else 100) + blast.score * 0.2 + (1 - rev.score) * 20
        )
        if budget and risk > budget.remaining:
            reasons.append(Reason.RISK_BUDGET_EXCEEDED)
        hard = {
            Reason.IDENTITY_INVALID,
            Reason.AGENT_QUARANTINED,
            Reason.EMERGENCY_STOP_ACTIVE,
            Reason.CAPABILITY_MISSING,
            Reason.POLICY_DENIED,
            Reason.HARD_POLICY,
            Reason.RISK_BUDGET_EXCEEDED,
            Reason.RED_TEAM_FAILED,
        }
        approval_required = po == Outcome.REQUIRE_HUMAN_APPROVAL or (
            action is not None and bool(action.human_approval_if)
        )
        if hard.intersection(reasons):
            outcome = Outcome.BLOCK
        elif reasons or approval_required:
            outcome = Outcome.REQUIRE_HUMAN_APPROVAL
        if self.human.rejected(mission_id):
            outcome = Outcome.BLOCK
            reasons.append(Reason.HUMAN_APPROVAL_REQUIRED)
        elif approval_required and not reasons and self.human.approved(mission_id):
            outcome = Outcome.ALLOW
        decision = GovernanceDecisionV2(
            mission_id=mission_id,
            agent_id=aid,
            outcome=outcome,
            reason_codes=tuple(dict.fromkeys(reasons)),
            evidence_refs=evidence_ids,
            policy_refs=policies,
            authority_context={
                "effective": self.authority.effective(agent, target) if agent else 0
            },
            risk_assessment={"score": risk, "trust": self.trust.get(aid).score},
            reversibility_assessment={"score": rev.score, "classification": rev.classification},
            blast_radius_assessment={"score": blast.score, "impacted": blast.impacted},
            constitution_version=self.version,
        )
        self.telemetry.increment("governance_decisions_total")
        self.telemetry.increment(f"governance_decisions_{outcome.value.lower()}_total")
        outcome_metric = {
            Outcome.ALLOW: "governance_allow_total",
            Outcome.BLOCK: "governance_block_total",
            Outcome.REQUIRE_HUMAN_APPROVAL: "governance_approval_required_total",
        }.get(outcome)
        if outcome_metric is not None:
            self.telemetry.increment(outcome_metric)
        for reason in decision.reason_codes:
            reason_name = reason.value.lower()
            if reason == Reason.CAPABILITY_MISSING:
                self.telemetry.increment("capability_denials_total")
            if reason == Reason.AUTHORITY_INSUFFICIENT:
                self.telemetry.increment("authority_denials_total")
            if reason in {Reason.POLICY_DENIED, Reason.HARD_POLICY}:
                self.telemetry.increment("policy_denials_total")
            if reason == Reason.EMERGENCY_STOP_ACTIVE:
                self.telemetry.increment("emergency_stop_blocks_total")
            if reason == Reason.AGENT_QUARANTINED:
                self.telemetry.increment("quarantine_blocks_total")
            self.telemetry.increment(f"governance_reason_{reason_name}_total")
        if outcome == Outcome.REQUIRE_HUMAN_APPROVAL:
            self.telemetry.increment("approval_requests_total")
        self.telemetry.emit(
            "governance.decision",
            mission_id=str(mission_id),
            agent_id=aid,
            action=action_type,
            scope=target,
            decision_id=str(decision.decision_id),
            outcome=outcome.value,
            reason_codes=",".join(reason.value for reason in decision.reason_codes),
        )
        self.telemetry.observe_latency("governance_evaluation", started_at)
        return decision
