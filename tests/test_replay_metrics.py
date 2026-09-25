from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from atlas.api.app import create_app
from atlas.domain.control import Outcome
from atlas.execution.authorization import ExecutionAuthorizationStore
from atlas.execution.service import ExecutionEnvelope, SafeExecutor
from atlas.observability import Telemetry
from atlas.shared.config import Settings

MISSION_ID = UUID("00000000-0000-0000-0000-000000000701")
DECISION_ID = UUID("00000000-0000-0000-0000-000000000702")
CORRELATION_ID = UUID("00000000-0000-0000-0000-000000000703")


class CountingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, action: str, params: dict[str, object]) -> dict[str, object]:
        self.calls += 1
        return {"success": True}


def envelope() -> ExecutionEnvelope:
    return ExecutionEnvelope(
        DECISION_ID,
        MISSION_ID,
        "replay-agent",
        datetime.now(UTC) + timedelta(minutes=1),
        "scope",
        {"mode": "safe"},
        None,
        CORRELATION_ID,
        action_type="replay-test",
    )


def test_metrics_endpoint_exports_counter_values_without_identifiers() -> None:
    app = create_app(Settings(constitution_path="config/constitution.json"))
    with TestClient(app) as client:
        telemetry = app.state.atlas.telemetry
        telemetry.increment("governance_decisions_total")
        telemetry.increment("emergency_stop_blocks_total")
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "governance_decisions_total 1" in response.text
    assert "emergency_stop_blocks_total 1" in response.text
    assert "human_approvals_total 0" in response.text
    assert "execution_replay_rejections_total 0" in response.text
    assert "mission_id" not in response.text
    assert "agent_id" not in response.text


def test_concurrent_execution_replay_allows_exactly_one_adapter_call() -> None:
    telemetry = Telemetry()
    adapter = CountingAdapter()
    executor = SafeExecutor(
        adapter, telemetry=telemetry, authorizations=ExecutionAuthorizationStore()
    )

    def execute() -> bool:
        try:
            executor.execute(Outcome.ALLOW, envelope(), "replay-test", {"mode": "safe"})
        except PermissionError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: execute(), range(16)))

    assert results.count(True) == 1
    assert adapter.calls == 1
    metrics = telemetry.metrics()
    assert metrics["execution_authorizations_consumed_total"] == 1
    assert metrics["execution_replay_rejections_total"] == 15


def test_failed_execution_consumes_authorization_before_adapter_invocation() -> None:
    class FailingAdapter:
        def execute(self, action: str, params: dict[str, object]) -> dict[str, object]:
            raise RuntimeError("simulated adapter failure")

    executor = SafeExecutor(FailingAdapter(), authorizations=ExecutionAuthorizationStore())
    issued = envelope()

    with pytest.raises(RuntimeError, match="adapter failure"):
        executor.execute(Outcome.ALLOW, issued, "replay-test", {"mode": "safe"})
    with pytest.raises(PermissionError, match="consumed"):
        executor.execute(Outcome.ALLOW, issued, "replay-test", {"mode": "safe"})
