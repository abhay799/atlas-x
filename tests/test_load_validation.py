from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from uuid import UUID

from atlas.control_plane.service import SupremeControlPlane
from atlas.domain.control import ActionDefinition, Outcome
from atlas.domain.models import AgentIdentity, AuthorityLevel
from atlas.governance.engines import Policy
from atlas.observability import Telemetry

MISSION_ID = UUID("00000000-0000-0000-0000-000000000601")


def test_bounded_concurrent_governance_load_records_mixed_outcomes() -> None:
    telemetry = Telemetry()
    plane = SupremeControlPlane("1.0", telemetry=telemetry)
    plane.actions.register(
        ActionDefinition(
            action_type="load-check",
            required_capabilities=frozenset({"load.read"}),
            minimum_authority=2,
            reversibility=1.0,
            default_risk=1.0,
            required_evidence=0,
        )
    )
    plane.policies.register(
        Policy("block-production", "1", 100, (("environment", "==", "production"),), Outcome.BLOCK)
    )
    plane.policies.register(
        Policy(
            "approval-staging",
            "1",
            50,
            (("environment", "==", "approval"),),
            Outcome.REQUIRE_HUMAN_APPROVAL,
        )
    )
    agent = AgentIdentity(
        agent_id="load-agent",
        role="test",
        authority=AuthorityLevel.L2,
        declared_capabilities=frozenset({"load.read"}),
        identity_provenance="test",
    )
    environments = ["staging", "production", "approval"] * 16

    def evaluate(environment: str) -> Outcome:
        return plane.evaluate(
            MISSION_ID,
            agent,
            "load-check",
            "load-scope",
            {"environment": environment, "rollback": True},
        ).outcome

    started_at = perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(evaluate, environments))
    elapsed = perf_counter() - started_at

    assert len(outcomes) == 48
    assert outcomes.count(Outcome.ALLOW) == 16
    assert outcomes.count(Outcome.BLOCK) == 16
    assert outcomes.count(Outcome.REQUIRE_HUMAN_APPROVAL) == 16
    assert elapsed > 0
    assert telemetry.metrics()["governance_decisions_total"] == 48
