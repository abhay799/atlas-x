# Observability, Resilience, and Replay Validation

## Objective

Validate lightweight local operational metrics, structured event export, and
single-use execution authorization without changing the ATLAS control plane or
adding distributed infrastructure.

## Instrumentation

`Telemetry` records structured governance and execution events without payload
contents. `EventSink` is the export boundary: `InMemoryEventSink` supports
tests and `StructuredLoggingSink` emits local structured log records. Future
OTLP or external export can implement the same interface.

## Metrics

`GET /metrics` renders the existing in-process counters and latency totals in
Prometheus text exposition format. It uses metric names only, with no mission,
agent, decision, or scope labels. Counters include governance outcomes, denial reasons,
approval requests, execution attempts/failures, authorization consumption, and
replay rejections.

## Load Environment

Local pytest execution on the Windows development machine using an 8-worker
thread pool. No production-scale or distributed-load claim is made.

## Workload and Results

The bounded load probe ran 48 concurrent deterministic evaluations: 16 ALLOW,
16 BLOCK, and 16 REQUIRE_HUMAN_APPROVAL. The focused run completed in 0.40
seconds including test-process overhead. A separate 32-request emergency-stop
probe returned BLOCK for every request.

## Failure Scenarios

- Configured database failure makes readiness return HTTP 503.
- Persistence failures surface to the caller.
- Execution denials and adapter failures increment failure metrics.
- Failed execution cannot legally transition to COMPLETED.
- Concurrent risk reservations remain bounded.
- A consumed execution authorization rejects replay.

## Replay Prevention

`ExecutionAuthorizationStore` atomically consumes an envelope decision ID
before adapter invocation. A crashed adapter does not make the authorization
reusable; retry requires a newly issued envelope. Sixteen concurrent attempts
against one envelope produced exactly one adapter call and fifteen replay
rejections.

## Known Limitations

- The authorization store and metrics are process-local; they do not provide
  distributed exactly-once semantics.
- No durable telemetry exporter, Prometheus server, or multi-process replay
  store is included.
- Duplicate replay prevention across process restarts requires a future
  persistence-backed atomic store.
- No production-readiness claim.

## Status

IMPLEMENTED_NOT_FULLY_VALIDATED. Local deterministic replay and metrics tests
pass, but complete certification requires a rerun with the isolated PostgreSQL
integration environment available to this session.
