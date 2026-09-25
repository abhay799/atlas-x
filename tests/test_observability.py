from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from atlas.api.app import create_app
from atlas.control_plane.service import SupremeControlPlane
from atlas.domain.control import ActionDefinition, Evidence, Outcome, Reason
from atlas.domain.models import AgentIdentity, AuthorityLevel
from atlas.execution.service import ExecutionEnvelope, SafeExecutor
from atlas.observability import Telemetry
from atlas.shared.config import Settings

MISSION_ID = UUID("00000000-0000-0000-0000-000000000401")
EVIDENCE_ID = UUID("00000000-0000-0000-0000-000000000402")


class FailingAdapter:
    def execute(self, action: str, params: dict[str, object]) -> dict[str, object]:
        raise TimeoutError("simulated timeout")


def agent(capabilities: frozenset[str] = frozenset({"observe.read"})) -> AgentIdentity:
    return AgentIdentity(
        agent_id="observer-agent",
        role="observer",
        authority=AuthorityLevel.L2,
        declared_capabilities=capabilities,
        identity_provenance="test",
    )


def configured_plane(telemetry: Telemetry) -> SupremeControlPlane:
    plane = SupremeControlPlane("1.0", telemetry=telemetry)
    plane.actions.register(
        ActionDefinition(
            action_type="observe",
            required_capabilities=frozenset({"observe.read"}),
            minimum_authority=2,
            reversibility=1.0,
            default_risk=1.0,
            required_evidence=1,
        )
    )
    plane.evidence.add(
        Evidence(
            evidence_id=EVIDENCE_ID,
            source="test",
            content_hash="observability",
            provenance="test",
            confidence=1.0,
            freshness_seconds=0,
            owner="test",
            trust_boundary="internal",
        )
    )
    return plane


def test_governance_metrics_and_reason_codes_are_recorded() -> None:
    telemetry = Telemetry()
    plane = configured_plane(telemetry)

    decision = plane.evaluate(
        MISSION_ID,
        agent(frozenset()),
        "observe",
        "scope",
        {"rollback": True},
        (EVIDENCE_ID,),
    )

    assert decision.outcome == Outcome.BLOCK
    assert Reason.CAPABILITY_MISSING in decision.reason_codes
    assert telemetry.metrics()["governance_decisions_total"] == 1
    assert telemetry.metrics()["governance_decisions_block_total"] == 1
    assert telemetry.metrics()["capability_denials_total"] == 1
    event = telemetry.events()[-1]
    assert event.name == "governance.decision"
    assert "CAPABILITY_MISSING" in event.fields["reason_codes"]


def test_execution_failure_and_denial_are_observable() -> None:
    telemetry = Telemetry()
    envelope = ExecutionEnvelope(
        UUID("00000000-0000-0000-0000-000000000403"),
        MISSION_ID,
        "observer-agent",
        datetime.now(UTC) + timedelta(minutes=1),
        "scope",
        {"mode": "safe"},
        None,
        UUID("00000000-0000-0000-0000-000000000404"),
        action_type="observe",
    )
    executor = SafeExecutor(FailingAdapter(), telemetry=telemetry)

    with pytest.raises(PermissionError):
        executor.execute(Outcome.BLOCK, envelope, "observe", {"mode": "safe"})
    with pytest.raises(TimeoutError, match="simulated timeout"):
        executor.execute(Outcome.ALLOW, envelope, "observe", {"mode": "safe"})

    metrics = telemetry.metrics()
    assert metrics["execution_attempts_total"] == 2
    assert metrics["execution_failures_total"] == 2
    assert {event.name for event in telemetry.events()} >= {
        "execution.denied",
        "execution.started",
        "execution.failed",
    }


def test_readiness_reflects_configured_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("atlas.api.app.database_is_ready", lambda url: False)
    app = create_app(
        Settings(
            constitution_path="config/constitution.json",
            database_url="postgresql+psycopg://atlas:local@localhost:54329/atlas_test",
        )
    )

    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").status_code == 503
