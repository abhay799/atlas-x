from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Any, Protocol
from uuid import UUID

from atlas.domain.control import Clock, Outcome
from atlas.execution.authorization import ExecutionAuthorizationStore
from atlas.observability import Telemetry


@dataclass(frozen=True)
class ExecutionEnvelope:
    decision_id: UUID
    mission_id: UUID
    agent_id: str
    expires_at: datetime
    scope: str
    allowed_parameters: dict[str, Any]
    rollback: str | None
    correlation_id: UUID
    action_type: str | None = None


class ExecutionAdapter(Protocol):
    def execute(
        self,
        action: str,
        params: dict[str, Any],
    ) -> dict[str, Any]: ...


class SimulationAdapter:
    def execute(
        self,
        action: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "simulated": True,
            "action": action,
            "params": params,
            "success": True,
        }


class SafeExecutor:
    def __init__(
        self,
        adapter: ExecutionAdapter,
        clock: Clock | None = None,
        telemetry: Telemetry | None = None,
        authorizations: ExecutionAuthorizationStore | None = None,
    ):
        self.adapter = adapter
        self.clock = clock or Clock()
        self.telemetry = telemetry or Telemetry()
        self.authorizations = authorizations or ExecutionAuthorizationStore()

    def execute(
        self,
        outcome: Outcome,
        envelope: ExecutionEnvelope,
        action: str,
        params: dict[str, Any],
        agent_id: str | None = None,
        mission_id: UUID | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        started_at = perf_counter()
        self.telemetry.increment("execution_attempts_total")
        try:
            return self._execute(outcome, envelope, action, params, agent_id, mission_id, scope)
        except PermissionError:
            self.telemetry.increment("execution_failures_total")
            if self.authorizations.consumed(envelope.decision_id) is not None:
                self.telemetry.increment("execution_replay_rejections_total")
            self.telemetry.emit("execution.denied", action=action, outcome=outcome.value)
            raise
        finally:
            self.telemetry.observe_latency("execution", started_at)

    def _execute(
        self,
        outcome: Outcome,
        envelope: ExecutionEnvelope,
        action: str,
        params: dict[str, Any],
        agent_id: str | None,
        mission_id: UUID | None,
        scope: str | None,
    ) -> dict[str, Any]:
        if not isinstance(envelope, ExecutionEnvelope):
            raise PermissionError("malformed execution envelope: invalid envelope instance")

        if not envelope.decision_id or not envelope.mission_id or not envelope.agent_id:
            raise PermissionError("malformed execution envelope: missing required identifiers")

        if outcome != Outcome.ALLOW:
            raise PermissionError("decision does not authorize execution")

        if self.clock.now() >= envelope.expires_at:
            raise PermissionError("execution envelope expired")

        if envelope.action_type is not None and action != envelope.action_type:
            raise PermissionError(
                f"action '{action}' does not match envelope action '{envelope.action_type}'"
            )

        if agent_id is not None and agent_id != envelope.agent_id:
            raise PermissionError(
                f"agent '{agent_id}' does not match execution envelope agent '{envelope.agent_id}'"
            )

        if mission_id is not None and mission_id != envelope.mission_id:
            raise PermissionError(
                f"mission '{mission_id}' does not match execution envelope "
                f"mission '{envelope.mission_id}'"
            )

        if scope is not None and scope != envelope.scope:
            raise PermissionError(
                f"scope '{scope}' does not match execution envelope scope '{envelope.scope}'"
            )

        invalid_parameters = any(
            key not in envelope.allowed_parameters or envelope.allowed_parameters[key] != value
            for key, value in params.items()
        )

        if invalid_parameters:
            raise PermissionError("parameters outside execution envelope")

        self.telemetry.emit(
            "execution.started",
            correlation_id=str(envelope.correlation_id),
            decision_id=str(envelope.decision_id),
            mission_id=str(envelope.mission_id),
            agent_id=envelope.agent_id,
            action=action,
            scope=envelope.scope,
            outcome=outcome.value,
        )

        self.authorizations.consume(envelope.decision_id, envelope.correlation_id)
        self.telemetry.increment("execution_authorizations_consumed_total")
        try:
            result = self.adapter.execute(action, params)
        except Exception:
            self.telemetry.increment("execution_failures_total")
            self.telemetry.emit("execution.failed", action=action, scope=envelope.scope)
            raise
        self.telemetry.emit("execution.verified", action=action, scope=envelope.scope)
        return result
