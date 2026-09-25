# ATLAS X

Autonomous AI Governance & Mission Control Fabric

ATLAS X is a typed Python control plane for deciding whether an autonomous
agent may perform a bounded action. It compiles missions, checks identity,
capability, authority, policy, evidence, risk, and human-control constraints,
then permits scoped simulation execution with audit and provenance evidence.

## Why ATLAS X Exists

An autonomous agent should never receive unlimited authority. ATLAS X answers:

- Who is this agent?
- What can it do, and under whose authority?
- Which policy, evidence, and risk constraints apply?
- Is human approval required?
- What happened after execution, and can the decision be reconstructed?

## Core Principle

**NO AGENT RECEIVES UNLIMITED AUTHORITY.**

## Governance Lifecycle

Objective → Mission → Identity → Capability → Authority → Policy → Context →
Trust → Conflict → Consensus → Evidence → Risk → Adversarial Challenge →
Counterfactual Analysis → Blast Radius → Reversibility → Risk Budget → Human
Approval when required → Safe Authorization → Execution → Verification →
Provenance → Audit.

## Architecture

ATLAS X is a modular monolith. `src/atlas/domain` owns typed contracts;
application, identity, capability, mission, and governance modules handle
proposal and authorization; safety, human-control, and security modules supply
constraints; `control_plane` composes the deterministic decision path;
`execution` enforces a scoped envelope over a simulation adapter; provenance,
audit, and infrastructure provide reconstruction and persistence.

## 30-Phase Roadmap

Phases 0–4 establish constitution, identity, capability, mission compilation,
and graph validation. Phases 5–12 cover teams, trust, authority, policy,
context, conflict, consensus, and correlation. Phases 13–19 cover provenance,
responsibility, adversarial review, counterfactuals, blast radius,
reversibility, and risk. Phases 20–28 add human control, emergency braking,
content defense, anomaly detection, quarantine, simulation, learning,
federation, and monitoring. Phase 29 certifies their local deterministic
control-plane composition.

## Phase 29 Certification

Thirteen focused deterministic tests within the 33-test local suite exercise a
coherent governed mission, negative governance cases, fixed-clock
execution-envelope checks, safe simulation execution, and
provenance/persistence reconstruction. This is local deterministic/simulation
certification, not a production certification.

## Security Model

ATLAS X fails closed: hard policy, emergency-stop, quarantine, and human
rejection dominate authorization. Approval is not a universal bypass; it can
resolve only a clean approval requirement with no unresolved governance reason
or hard block. Execution authorization is scoped by decision, expiry, action,
agent, mission, scope, and allowed parameters where supplied.

## Technology Stack

Python, FastAPI, Pydantic, SQLAlchemy, Alembic, pytest, mypy, Ruff, and
psycopg for local PostgreSQL integration. PostgreSQL persistence and the
Alembic migration lifecycle have been validated against an isolated local
PostgreSQL 17 container.

## Repository Structure

```text
src/atlas/       domain, governance, safety, execution, and API modules
tests/           foundation, API, migration, Phase 29, and PostgreSQL tests
migrations/      Alembic environment and revisions
compose.yaml     development-only PostgreSQL service
docs/            architecture, security, testing, and status evidence
```

## Running Locally

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -v
mypy src
ruff check .
uvicorn atlas.api.app:app --reload
```

## Public Demo Deployment

Document:
- local backend command
- Docker build/run
- Railway start configuration
- required environment variables
  - ATLAS_CORS_ORIGINS must contain the browser frontend origin(s), for example:
    https://atlas-x.vercel.app (not the Railway backend's own URL).
  - Local example remains: http://localhost:3000

- /health
- /ready
- current public-demo scope

State clearly:
ATLAS X public demo demonstrates governance and mission-control workflows using deterministic/synthetic scenarios.

Do NOT claim:
- production autonomous agent execution
- quarantine
- emergency braking
- prompt-injection defense
- production-scale multi-agent deployment
unless those are actually implemented.

## PostgreSQL Validation

```powershell
docker compose up -d postgres
$env:ATLAS_POSTGRES_TEST_URL = "postgresql+psycopg://atlas:atlas-local-only@localhost:54329/atlas_test"
alembic upgrade head
pytest -v tests/integration/test_postgres_persistence.py
docker compose down
```

The integration test validates upgrade/current, downgrade/re-upgrade,
migration-created schema, SQLStore persistence, structured payloads, rollback,
and primary-key integrity against the isolated local container.

## Validation Results

Local engineering validation: 33 tests passed, including 1 PostgreSQL
integration test; mypy reported 0 issues across 35 source files; Ruff passed;
SQLite and isolated local PostgreSQL Alembic lifecycle checks passed. These are
not external, HA, cloud, or production certifications.

## Limitations

- Local PostgreSQL certification only.
- No HA, replication, failover, or cloud-managed PostgreSQL validation.
- Simulation execution adapter only; no destructive production adapters.
- No multi-node ATLAS deployment validation.
- Audit/provenance is not yet cryptographically tamper-evident.
- No production-readiness claim.

## Future Work

- HA and cloud PostgreSQL validation.
- Durable production adapters.
- Distributed execution validation.
- Stronger observability, load testing, and adversarial testing.

## Portfolio Positioning

ATLAS X demonstrates backend architecture, deterministic policy enforcement,
security boundaries, typed Python, auditability/provenance, safe
autonomous-system design, and testing discipline. Its documented scope is the
validated local control plane, not an asserted production deployment.
