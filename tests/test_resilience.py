from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest

from atlas.control_plane.service import SupremeControlPlane
from atlas.domain.control import ActionDefinition, Evidence, GovState, Outcome, transition
from atlas.domain.models import AgentIdentity, AuthorityLevel
from atlas.infrastructure.db import SQLStore
from atlas.safety.engines import RiskBudget

MISSION_ID = UUID("00000000-0000-0000-0000-000000000501")


def agent() -> AgentIdentity:
    return AgentIdentity(
        agent_id="resilience-agent",
        role="test",
        authority=AuthorityLevel.L2,
        declared_capabilities=frozenset({"resilience.read"}),
        identity_provenance="test",
    )


def configured_plane() -> SupremeControlPlane:
    plane = SupremeControlPlane("1.0")
    plane.actions.register(
        ActionDefinition(
            action_type="resilience",
            required_capabilities=frozenset({"resilience.read"}),
            minimum_authority=2,
            reversibility=1.0,
            default_risk=1.0,
            required_evidence=1,
        )
    )
    evidence = Evidence(
        source="test",
        content_hash="resilience",
        provenance="test",
        confidence=1.0,
        freshness_seconds=0,
        owner="test",
        trust_boundary="internal",
    )
    plane.evidence.add(evidence)
    plane.emergency.stop_mission(MISSION_ID)
    return plane


def test_emergency_stop_dominates_bounded_concurrent_evaluations() -> None:
    plane = configured_plane()
    evidence_id = next(iter(plane.evidence.items))

    def evaluate() -> Outcome:
        return plane.evaluate(
            MISSION_ID,
            agent(),
            "resilience",
            "scope",
            {"rollback": True},
            (evidence_id,),
        ).outcome

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(lambda _: evaluate(), range(32)))
    assert outcomes == [Outcome.BLOCK] * 32


def test_risk_budget_reservations_remain_bounded_under_concurrency() -> None:
    budget = RiskBudget(5.0)

    def reserve() -> bool:
        try:
            budget.reserve(1.0)
        except ValueError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = list(pool.map(lambda _: reserve(), range(16)))
    assert accepted.count(True) == 5
    assert budget.remaining == 0.0


def test_persistence_failure_is_surfaced() -> None:
    store = SQLStore()

    class BrokenSessionFactory:
        def begin(self) -> None:
            raise RuntimeError("simulated persistence failure")

    store.Session = BrokenSessionFactory()
    with pytest.raises(RuntimeError, match="persistence failure"):
        store.append("audit", "failure", {"outcome": "BLOCK"})


def test_failed_execution_cannot_reach_completed() -> None:
    assert transition(GovState.EXECUTING, GovState.FAILED) == GovState.FAILED
    with pytest.raises(ValueError):
        transition(GovState.FAILED, GovState.COMPLETED)
