# Development

ATLAS X requires Python 3.12 or newer. Local validation was performed with
Python 3.14.5 on Windows.

## PowerShell Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` only for local configuration. Environment names
use the `ATLAS_` prefix; never commit credentials.

## Database Migrations

`ATLAS_DATABASE_URL` selects the Alembic database URL. SQLite remains useful
for lightweight tests. PostgreSQL persistence and the Alembic migration
lifecycle have been validated against an isolated local PostgreSQL 17
container, using `psycopg[binary]` 3.3.6.

```powershell
alembic upgrade head
alembic current
alembic history
alembic downgrade base
```

Review and back up production data before downgrade. Migration failures are
intentionally surfaced to the operator.

## Local PostgreSQL Certification Setup

`compose.yaml` defines an isolated development-only PostgreSQL 17 service on
port `54329`. Its default password is local-only and may be overridden with
`ATLAS_POSTGRES_PASSWORD`; it is not a production credential.

```powershell
docker compose up -d postgres
$env:ATLAS_POSTGRES_TEST_URL = "postgresql+psycopg://atlas:atlas-local-only@localhost:54329/atlas_test"
pytest -v tests/integration/test_postgres_persistence.py
docker compose down
```

Use only a dedicated `*_test` database URL. The integration test performs
upgrade/downgrade operations and refuses URLs that are not PostgreSQL psycopg
test databases. The validation does not cover HA, replication, failover,
cloud-managed PostgreSQL, or production deployment.

## Validation

```powershell
pytest -v
mypy src
ruff check .
python -c "from atlas.api.app import app; print(app.title, app.version)"
```

Latest local gates: 33 tests passed, including 1 PostgreSQL integration test;
mypy reported 0 issues across 35 source files; Ruff passed. Keep mypy strict
and Ruff enabled, preserve fail-closed governance semantics, and add
deterministic regression coverage for behavior changes.
