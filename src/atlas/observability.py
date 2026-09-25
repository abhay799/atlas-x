from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from time import perf_counter
from typing import Protocol

type EventValue = str | int | float | bool | None

_EXPORTED_COUNTERS = (
    "governance_decisions_total",
    "governance_allow_total",
    "governance_block_total",
    "governance_approval_required_total",
    "policy_denials_total",
    "capability_denials_total",
    "authority_denials_total",
    "emergency_stop_blocks_total",
    "quarantine_blocks_total",
    "approval_requests_total",
    "human_approvals_total",
    "human_rejections_total",
    "execution_attempts_total",
    "execution_failures_total",
    "execution_replay_rejections_total",
    "execution_authorizations_consumed_total",
    "governance_evaluation_latency_seconds_count",
    "governance_evaluation_latency_seconds_total",
    "execution_latency_seconds_count",
    "execution_latency_seconds_total",
)


@dataclass(frozen=True)
class ObservabilityEvent:
    name: str
    timestamp: datetime
    fields: dict[str, str]


class EventSink(Protocol):
    def emit(self, event: ObservabilityEvent) -> None: ...


class InMemoryEventSink:
    def __init__(self) -> None:
        self._events: list[ObservabilityEvent] = []
        self._lock = Lock()

    def emit(self, event: ObservabilityEvent) -> None:
        with self._lock:
            self._events.append(event)

    def events(self) -> tuple[ObservabilityEvent, ...]:
        with self._lock:
            return tuple(self._events)


class StructuredLoggingSink:
    def __init__(self) -> None:
        self._logger = logging.getLogger("atlas.observability")

    def emit(self, event: ObservabilityEvent) -> None:
        payload = json.dumps({"event": event.name, **event.fields}, sort_keys=True)
        self._logger.info("atlas_event=%s", payload)


class Telemetry:
    """Small in-process structured event and counter recorder."""

    def __init__(self, sinks: tuple[EventSink, ...] | None = None) -> None:
        self._memory_sink = InMemoryEventSink()
        configured_sinks = sinks or (StructuredLoggingSink(),)
        self._sinks: tuple[EventSink, ...] = (self._memory_sink, *configured_sinks)
        self._metrics: Counter[str] = Counter()
        self._latency_totals: dict[str, float] = {}
        self._lock = Lock()

    def emit(self, name: str, **fields: EventValue) -> None:
        normalized = {key: str(value) for key, value in fields.items() if value is not None}
        event = ObservabilityEvent(name, datetime.now(UTC), normalized)
        for sink in self._sinks:
            sink.emit(event)

    def increment(self, name: str) -> None:
        with self._lock:
            self._metrics[name] += 1

    def observe_latency(self, prefix: str, started_at: float) -> None:
        elapsed = perf_counter() - started_at
        with self._lock:
            self._metrics[f"{prefix}_latency_seconds_count"] += 1
            total_name = f"{prefix}_latency_seconds_total"
            self._latency_totals[total_name] = self._latency_totals.get(total_name, 0.0) + elapsed

    def events(self) -> tuple[ObservabilityEvent, ...]:
        return self._memory_sink.events()

    def metrics(self) -> dict[str, float]:
        with self._lock:
            return {
                **{name: 0.0 for name in _EXPORTED_COUNTERS},
                **{name: float(value) for name, value in self._metrics.items()},
                **self._latency_totals,
            }
