# Architecture

ATLAS X is a modular monolith. Typed domain contracts are independent of
FastAPI and persistence; bounded contexts communicate through explicit Python
models and services rather than networked infrastructure.

```text
External/API Layer (atlas.api, FastAPI)
        ↓
Mission / Identity / Capability (application, missions, identity, capabilities)
        ↓
Governance Kernel (constitution, gateway, governance engines)
        ↓
Risk & Safety (safety, security)
        ↓
Human Control (human_control)
        ↓
Supreme Control Plane (control_plane)
        ↓
Safe Execution Envelope (execution)
        ↓
Simulation Adapter (execution, simulation)
        ↓
Verification / Provenance / Persistence (provenance, infrastructure)
```

## Bounded Contexts

- `domain`: immutable Pydantic contracts, outcomes, reasons, and state
  transitions.
- `application`: the `AtlasService` boundary for mission compilation, identity,
  capabilities, gateway decisions, and audit events.
- `governance`: constitution loading, policy, authority, trust, conflict,
  consensus, evidence, and action registries.
- `safety`, `security`, and `human_control`: risk, reversibility, blast radius,
  red-team checks, content defense, quarantine, approval, and emergency stop.
- `control_plane`: deterministic composition of governance checks.
- `execution`: execution-envelope and simulation-adapter boundary.
- `provenance` and `infrastructure`: in-memory audit/graph reconstruction and
  the existing SQLAlchemy record store.

## Proposal, Authorization, and Execution

A proposal is mission/task intent. Authorization is a governance decision;
`ALLOW`, `REQUIRE_HUMAN_APPROVAL`, and `BLOCK` are separate from execution.
Execution requires an `ALLOW` decision plus an unexpired, scoped envelope.
This separation is a security boundary: a proposal cannot invoke an adapter
directly, and an authorization alone is not an unconstrained operation.

The current certified adapter is `SimulationAdapter`. Production adapters,
distributed orchestration, and PostgreSQL runtime certification are outside
the validated scope.
