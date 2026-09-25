# Testing

ATLAS X has 33 locally passing tests: bounded-context tests, API/persistence
integration tests, SQLite migration lifecycle coverage, 13 Phase 29
certification tests, and 1 PostgreSQL integration test.

## Test Categories

- **Unit and bounded-context tests:** contracts, identity, capabilities,
  mission DAGs, authority, policy, safety, human control, learning,
  federation, and monitoring.
- **Integration tests:** FastAPI bootstrap flow, SQLAlchemy record retrieval,
  and Alembic migration lifecycle tests.
- **Certification tests:** deterministic end-to-end governed simulation,
  precedence controls, negative fail-closed cases, execution-envelope binding,
  provenance, audit, and persistence evidence.

The Phase 29 suite uses an injected fixed clock and simulation-only execution;
it does not sleep or invoke real destructive operations.

## Commands

```powershell
pytest -v
pytest -v tests/test_phase29_certification.py
pytest -v tests/integration/test_postgres_persistence.py
mypy src
ruff check .
```

## PostgreSQL Integration

PostgreSQL persistence and the Alembic migration lifecycle have been validated
against an isolated local PostgreSQL 17 container. The single integration test
verified connection/schema availability, base-to-head upgrade, current/head
revision, downgrade, re-upgrade, SQLStore insert/retrieval, structured payload
persistence, transaction rollback, and primary-key integrity.

Run the test only against the dedicated URL:

```powershell
docker compose up -d postgres
$env:ATLAS_POSTGRES_TEST_URL = "postgresql+psycopg://atlas:atlas-local-only@localhost:54329/atlas_test"
pytest -v tests/integration/test_postgres_persistence.py
docker compose down
```

The test refuses non-`*_test` PostgreSQL psycopg URLs. This validation does not
cover HA, replication, failover, cloud-managed PostgreSQL, or production
operations.
