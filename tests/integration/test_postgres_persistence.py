from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError

from atlas.infrastructure.db import Record, SQLStore

ROOT = Path(__file__).resolve().parents[2]
REVISION = "0001_records"


def postgres_test_url() -> str:
    url = os.environ.get("ATLAS_POSTGRES_TEST_URL")
    if not url:
        pytest.skip(
            "PostgreSQL certification is pending: set ATLAS_POSTGRES_TEST_URL "
            "to an isolated test database"
        )
    parsed = urlparse(url)
    if parsed.scheme != "postgresql+psycopg" or not parsed.path.rstrip("/").endswith("_test"):
        pytest.fail("ATLAS_POSTGRES_TEST_URL must be a postgresql+psycopg isolated *_test database")
    return url


def alembic_config(url: str) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_postgres_migration_and_sqlstore_lifecycle() -> None:
    url = postgres_test_url()
    config = alembic_config(url)
    engine = create_engine(url)

    try:
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert MigrationContext.configure(connection).get_current_revision() == REVISION

        inspector = inspect(engine)
        assert set(inspector.get_table_names()) >= {"alembic_version", "atlas_records"}
        assert {column["name"] for column in inspector.get_columns("atlas_records")} == {
            "id",
            "kind",
            "key",
            "payload",
            "created_at",
        }
        assert {index["name"] for index in inspector.get_indexes("atlas_records")} == {
            "ix_atlas_records_key",
            "ix_atlas_records_kind",
        }

        store = SQLStore(url)
        store.append("decision", "postgres-certification", {"outcome": "ALLOW", "score": 0.9})
        assert store.list("decision", "postgres-certification") == [
            {"outcome": "ALLOW", "score": 0.9}
        ]

        with store.Session() as session:
            session.add(Record(kind="rollback", key="discarded", payload="{}"))
            session.rollback()
        assert store.list("rollback", "discarded") == []

        with pytest.raises(IntegrityError):
            with store.Session.begin() as session:
                session.add(Record(id=9001, kind="primary-key", key="first", payload="{}"))
                session.add(Record(id=9001, kind="primary-key", key="duplicate", payload="{}"))

        command.downgrade(config, "base")
        assert "atlas_records" not in inspect(engine).get_table_names()
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert MigrationContext.configure(connection).get_current_revision() == REVISION
    finally:
        command.downgrade(config, "base")
        engine.dispose()
