# ATLAS X Alembic migrations

Alembic uses `atlas.infrastructure.db.Base.metadata` as its only schema source.
Do not add migration-only ORM models or call `Base.metadata.create_all()` as a
production migration mechanism.

`versions/0001_records.py` is the executable Alembic baseline for the existing
`atlas_records` SQLAlchemy model. The prior `versions/0001_records.sql` file is
retained unchanged as historical reference: it predates Alembic and is not
loaded by Alembic's Python revision scanner. It used one composite index,
whereas the executable revision matches the current ORM metadata's two named
single-column indexes. A database created solely from the legacy SQL must be
reviewed before it is stamped as `0001_records`; do not stamp an unknown schema.

For a fresh local database:

```powershell
$env:ATLAS_DATABASE_URL = "sqlite+pysqlite:///atlas-x.db"
alembic upgrade head
alembic current
```

For PostgreSQL, set `ATLAS_DATABASE_URL` to a SQLAlchemy PostgreSQL URL, such
as `postgresql+psycopg://atlas_x:password@db.example/atlas_x`, using your
deployment secret store. Install the corresponding PostgreSQL DBAPI driver in
the deployment environment; credentials must never be committed.

To roll back the baseline, run `alembic downgrade base`. Review the target
revision and back up production data before any downgrade; migration failures
are intentionally returned to the operator.
