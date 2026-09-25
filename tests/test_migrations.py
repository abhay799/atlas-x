from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[1]


def test_initial_migration_upgrades_and_downgrades_sqlite(tmp_path: Path) -> None:
    database_path = tmp_path / "atlas.db"
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path.as_posix()}")

    command.upgrade(config, "head")

    engine = create_engine(config.get_main_option("sqlalchemy.url"))
    inspector = inspect(engine)
    assert "atlas_records" in inspector.get_table_names()
    assert {index["name"] for index in inspector.get_indexes("atlas_records")} == {
        "ix_atlas_records_key",
        "ix_atlas_records_kind",
    }

    command.downgrade(config, "base")
    assert "atlas_records" not in inspect(engine).get_table_names()
